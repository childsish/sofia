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
            for in_, out in ((path[0], path[-1]) for path in self.entity_graph.getAncestorPaths(in_) if len(path) == 2):
                extractor_name = 'Extract%sFrom%s'%\
                        (getEntityName(out), getEntityName(in_))
                extractor = FeatureWrapper(Extractor,
                    extractor_name,
                    ins={in_: self.entity_graph.createEntity(in_)},
                    outs={out: self.entity_graph.createEntity(out)},
                    kwargs={'path': [in_, out]})
                self.features[extractor_name] = extractor
                self.graph.addVertex(extractor_name)
                self.graph.addEdge(in_, extractor_name)
                self.ins[in_].add(extractor_name)
                for in_origin in self.outs[in_]:
                    self.graph.addEdge(in_, extractor_name, in_origin)
                self.outs[out].add(extractor_name)
                for out_destination in self.ins[out]:
                    self.graph.addEdge(out, out_destination, extractor_name)

        for out in feature.outs:
            self.outs[out].add(c_feature)
            for out_destination in self.ins[out]:
                self.graph.addEdge(out, out_destination, c_feature)
        
        if feature.feature_class is not Converter and\
                issubclass(feature.feature_class, Converter):
            convertee = list(set(feature.ins) & set(feature.outs))[0]
            id_map = list(set(feature.ins) - set(feature.outs))[0]
            for path in self.entity_graph.getAncestorPaths(convertee):
                converter_name = 'Convert%sIn%s'%\
                        (getEntityName(path[-1]), getEntityName(path[0]))
                converter = FeatureWrapper(feature.feature_class,
                    converter_name,
                    ins=[path[0], id_map],
                    outs={path[0]: self.entity_graph.createEntity(path[0])},
                    kwargs={'path': path, 'map': id_map})
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
        #print feature_name
        
        if issubclass(feature.feature_class, Resource):
            if issubclass(feature.feature_class, Target) and feature.feature_class.matches(resources['target']):
                for outs in feature.iterOutput({'resource': resources['target']}):
                    res = self.initFeatureGraph(feature, outs, resources['target'])
                    #print '', feature_name, res.feature.getAttributes()
                    yield res
            elif not issubclass(feature.feature_class, Target):
                hits = set(resource for resource in resources.itervalues()\
                    if resource.name != 'target' and feature.feature_class.matches(resource))
                for hit in hits:
                    for outs in feature.iterOutput({'resource': hit}):
                        #print '', feature_name
                        yield self.initFeatureGraph(feature, outs, hit)
            raise StopIteration()
        
        edge_names = sorted(self.graph.vs[feature_name].iterkeys())
        for partial_solutions, ins in self.iterDependencies(feature_name, 0, {}, [], requested_feature, resources, visited):
            ins = {edge: partial_solution.feature.outs[edge] for edge, partial_solution in izip(edge_names, partial_solutions)}
            for outs in feature.iterOutput(ins):
                resources_ = reduce(or_, (graph.resources for graph in partial_solutions))
                dependencies = {edge: partial_solution.feature.name for edge, partial_solution in izip(edge_names, partial_solutions)}
                kwargs = requested_feature.args\
                    if requested_feature.name == feature_name else {}
                feature_instance = feature(resources_, dependencies, kwargs, ins, outs)
                res = FeatureGraph(feature_instance)
                for edge, partial_solution in izip(edge_names, partial_solutions):
                    res.addEdge(edge, feature_instance.name, partial_solution.feature.name)
                    res.update(partial_solution)
                #print 'Here', feature_name
                #print [(edge, partial_solution.feature.name) for edge, partial_solution in izip(edge_names, partial_solutions)]
                #print [(edge, partial_solution.feature.outs[edge].attr) for edge, partial_solution in izip(edge_names, partial_solutions)]
                #print res.feature.getAttributes()
                #print res
                yield res

    def iterDependencies(self, feature_name, edge_idx, outs, solution, requested_feature, resources, visited):
        edge_names = sorted(self.graph.vs[feature_name].iterkeys())
        if edge_idx == len(edge_names):
            yield solution, outs
            raise StopIteration()
        edge_name = edge_names[edge_idx]
        for dep in self.graph.vs[feature_name][edge_name]:
            found_partial_solution = False
            for partial_solution in self.iterFeatureGraphs(dep, requested_feature, resources, set(visited)):
                if not self.outputsMatch(outs, partial_solution.feature.outs[edge_name].attr):
                    ERROR_MANAGER.addError('%s resolving edge %s: %s attributes conflicts with partial solution. %s vs. %s'%\
                        (feature_name, edge_name, dep, partial_solution.feature.outs[edge_name].attr, outs))
                    continue
                found_partial_solution = True
                outs.update(partial_solution.feature.outs[edge_name].attr)
                solution.append(partial_solution)
                for graph, outs_ in self.iterDependencies(feature_name, edge_idx + 1, outs, solution, requested_feature, resources, visited):
                    yield graph, outs_
            if not found_partial_solution:
                ERROR_MANAGER.addError('%s can not resolve dependency: %s'%(feature_name, dep))
        
    def outputsMatch(self, out_a, out_b):
        for name in set(out_a) & set(out_b):
            if out_a[name] != out_b[name]:
                return False
        return True
        
    def initFeatureGraph(self, feature, outs, resource):
        """ Create a single node FeatureGraph. """
        feature_instance = feature(set([resource]), {}, resource.param, {}, outs)
        res = FeatureGraph(feature_instance)
        res.addResource(resource)
        return res
