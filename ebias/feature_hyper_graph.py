from collections import defaultdict
from itertools import product, izip
from operator import or_

from lhc.graph.hyper_graph import HyperGraph
from error_manager import ERROR_MANAGER
from feature_graph import FeatureGraph
from feature_wrapper import FeatureWrapper
from features import Resource, Target, Extractor, Converter

class FeatureHyperGraph(object):
    """ A hyper graph of all the possible feature calculation pathways. """
    def __init__(self, entity_graph):
        self.outs = defaultdict(set)
        self.ins = defaultdict(set)
        self.features = {}
        self.graph = HyperGraph()
        self.entity_graph = entity_graph
    
    def __str__(self):
        """ Returns a dot formatted representation of the graph. """
        return str(self.graph)
    
    def registerFeature(self, feature):
        """ Add a feature to the hyper graph. """
        def getEntityName(entity):
            return ''.join(part.capitalize() for part in entity.split('_')).replace('*', '')
        
        c_feature = feature.name
        self.features[c_feature] = feature
        self.graph.addVertex(c_feature)
        
        for in_ in feature.ins:
            self.ins[in_].add(c_feature)
            self.graph.addEdge(in_, c_feature)
            for in_origin in self.outs[in_]:
                self.graph.addEdge(in_, c_feature, in_origin)
            for path in self.entity_graph.getAncestorPaths(in_):
                if len(path) != 2:
                    continue
                extractor_name = 'Extract%sFrom%s'%\
                        (getEntityName(path[-1]), getEntityName(path[0]))
                extractor = FeatureWrapper(Extractor,
                    extractor_name,
                    ins=[path[0]],
                    outs=[path[-1]],
                    kwargs={'path': path})
                self.features[extractor_name] = extractor
                self.graph.addVertex(extractor_name)
                self.graph.addEdge(path[0], extractor_name)
                for in_ in extractor.ins:
                    self.ins[in_].add(extractor_name)
                    for in_origin in self.outs[in_]:
                        self.graph.addEdge(in_, extractor_name, in_origin)
                self.outs[path[-1]].add(extractor_name)
                for out_destination in self.ins[path[-1]]:
                    self.graph.addEdge(path[-1], out_destination, extractor_name)

        for out in feature.outs:
            self.outs[out].add(c_feature)
            for out_destination in self.ins[out]:
                self.graph.addEdge(out, out_destination, c_feature)
            for path in self.entity_graph.getDescendentPaths(out):
                if len(path) != 2:
                    continue
                extractor_name = 'Extract%sFrom%s'%\
                        (getEntityName(path[-1]), getEntityName(path[0]))
                extractor = FeatureWrapper(Extractor,
                    extractor_name,
                    ins=[path[0]],
                    outs=[path[-1]],
                    kwargs={'path': path})
                self.features[extractor_name] = extractor
                self.graph.addVertex(extractor_name)
                self.graph.addEdge(path[0], extractor_name)
                for in_ in extractor.ins:
                    self.ins[in_].add(extractor_name)
                    for in_origin in self.outs[in_]:
                        self.graph.addEdge(in_, extractor_name, in_origin)
                self.outs[path[-1]].add(extractor_name)
                for out_destination in self.ins[path[-1]]:
                    self.graph.addEdge(path[-1], out_destination, extractor_name)
        
        if feature.feature_class is not Converter and\
                issubclass(feature.feature_class, Converter):
            convertee = list(set(feature.ins) & set(feature.outs))[0]
            id_map = list(set(feature.ins) - set(feature.outs))[0]
            for path in self.entity_graph.getAncestorPaths(convertee):
                converter_name = 'Convert%sIn%s'%\
                        (getEntityName(path[-1]), getEntityName(path[0]))
                converter = FeatureWrapper(Converter,
                    converter_name,
                    ins=[path[0], id_map],
                    outs=[path[0]],
                    kwargs={'path': path})
                self.features[converter_name] = converter
                self.graph.addVertex(converter_name)
                self.graph.addEdge(path[0], converter_name)
                for in_ in converter.ins:
                    self.ins[in_].add(converter_name)
                    for in_origin in self.outs[in_]:
                        self.graph.addEdge(in_, converter_name, in_origin)
                self.outs[path[0]].add(converter_name)
                for out_destination in self.ins[path[0]]:
                    self.graph.addEdge(path[0], out_destination, converter_name)


    def iterFeatureGraphs(self, feature_name, requested_feature, resources, visited=None):
        """ Find all possible resolutions for the given feature_name. """
        if visited is None:
            visited = set()
        elif feature_name in visited:
            raise StopIteration()
        visited.add(feature_name)
        feature = self.features[feature_name]
        
        if issubclass(feature.feature_class, Resource):
            if issubclass(feature.feature_class, Target) and feature.matches(resources['target']):
                yield self.initFeatureGraph(feature, resources['target'])
            elif not issubclass(feature.feature_class, Target):
                hits = set(resource for resource in resources.itervalues()\
                    if resource.name != 'target' and feature.feature_class.matches(resource))
                for hit in hits:
                    yield self.initFeatureGraph(feature.feature_class, hit)
            raise StopIteration()
        
        edge_names = sorted(self.graph.vs[feature_name].iterkeys())
        edge_dependencies = []
        for edge_name in edge_names:
            edge_dependencies.append(list(self.iterDependencies(self.graph.vs[feature_name][edge_name], requested_feature, resources, visited)))
        
        missing_dependencies = [name for name, dependencies in izip(edge_names, edge_dependencies) if len(dependencies) == 0]
        if len(missing_dependencies) > 0:
            ERROR_MANAGER.addError('%s is missing dependencies: %s'%(feature_name, ','.join(missing_dependencies)))
        
        for cmb in product(*edge_dependencies):
            resources = reduce(or_, (graph.resources for name, graph in cmb))
            dependencies = {edge: dependee_graph.feature.getName() for edge, (dependee, dependee_graph) in izip(edge_names, cmb)}
            kwargs = requested_feature.args\
                if requested_feature.name == feature_name else {}
            feature_instance = feature(resources, dependencies, kwargs)
            res = FeatureGraph(feature_instance)
            for edge, (dependee, dependee_graph) in izip(edge_names, cmb):
                res.addEdge(edge, feature_instance.getName(), dependee)
                res.update(dependee_graph)
            yield res
    
    def iterDependencies(self, dependencies, requested_feature, resources, visited):
        """ Iterate through all the solutions for each dependency of a single
        edge. """
        for dependency in dependencies:
            for dependency_graph in self.iterFeatureGraphs(dependency, requested_feature, resources, set(visited)):
                yield (dependency, dependency_graph)

    def initFeatureGraph(self, feature, resource):
        """ Create a single node FeatureGraph. """
        feature_instance = feature(set([resource]), kwargs=resource.init_args)
        res = FeatureGraph(feature_instance)
        res.addResource(resource)
        return res
