from collections import defaultdict
from itertools import product, izip
from operator import or_

from lhc.graph.hyper_graph import HyperGraph
from ebias.feature_graph import FeatureGraph
from ebias.resource import Resource

class FeatureHyperGraph(object):
    def __init__(self):
        self.outs = defaultdict(set)
        self.ins = defaultdict(set)
        self.features = {}
        self.graph = HyperGraph()
    
    def __str__(self):
        return str(self.graph)
    
    def registerFeature(self, feature):
        name = feature.__name__
        self.features[name] = feature
        self.graph.addVertex(name)
        
        for in_ in feature.IN:
            self.ins[in_].add(name)
            self.graph.addEdge(in_, name)
            for child in self.outs[in_]:
                self.graph.addEdge(in_, name, child)
        for out in feature.OUT:
            self.outs[out].add(name)
            for parent in self.ins[out]:
                self.graph.addEdge(out, parent, name)

    def iterFeatureGraphs(self, feature_name, resources, visited, kwargs={}):
        if feature_name in visited:
            raise StopIteration()
        visited.add(feature_name)
        feature = self.features[feature_name]
        if issubclass(feature, Resource):
            if feature.TARGET and feature.matches(resources['target']):
                yield self.initFeatureGraph(feature, set([resources['target']]))
            elif not feature.TARGET:
                hits = set(resource for resource in resources.itervalues() if resource.name != 'target' and feature.matches(resource))
                if len(hits) > 1:
                    raise ValueError('Multiple resources possible')
                elif len(hits) == 1:
                    yield self.initFeatureGraph(feature, hits)
            raise StopIteration()
        
        edge_names = sorted(self.graph.vs[feature_name].iterkeys())
        edge_dependencies = [list(self.iterDependencies(self.graph.vs[feature_name][edge], resources, set(visited))) for edge in edge_names]
        
        #TODO: Check here for missing dependencies
        
        for cmb in product(*edge_dependencies):
            resources = reduce(or_, (graph.resources for name, graph in cmb))
            dependencies = {edge: dependee_graph.feature.getName() for edge, (dependee, dependee_graph) in izip(edge_names, cmb)}
            feature_instance = feature(resources, dependencies)
            feature_instance.init(**kwargs)
            res = FeatureGraph(feature_instance)
            for edge, (dependee, dependee_graph) in izip(edge_names, cmb):
                res.addEdge(edge, feature_instance.getName(), dependee)
                res.update(dependee_graph)
            yield res
    
    def iterDependencies(self, dependencies, resources, visited):
        # Each edge may have several dependencies and each dependency may have several resolutions
        for dependency in dependencies:
            for dependency_graph in self.iterFeatureGraphs(dependency, resources, visited):
                yield (dependency, dependency_graph)

    def initFeatureGraph(self, feature, resources):
        feature_instance = feature(resources)
        feature_instance.init() #TODO: feature initialisation arguments
        res = FeatureGraph(feature_instance)
        for resource in resources:
            res.addResource(resource)
        return res
        
