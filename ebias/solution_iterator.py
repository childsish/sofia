from collections import defaultdict
from feature_graph import FeatureGraph
from itertools import izip, repeat, product
from operator import or_

from ebias.features import Resource, Target
from ebias.error_manager import ERROR_MANAGER

class SolutionIterator(object):
    def __init__(self, feature, graph, provided_resources, visited=None):
        self.feature = feature
        self.graph = graph
        self.resources = provided_resources
        self.visited = set() if visited is None else visited

        self.visited.add(self.feature.name)

    def __str__(self):
        return self.feature.name
    
    def __iter__(self):
        for solution in self.iterFeature():
            yield solution

    def iterFeature(self):
        edges = sorted(self.graph.vs[self.feature.name])
        solutions = [list(self.iterEdge(edge)) for edge in edges]

        cnt = defaultdict(list)
        for edge, edge_solutions in izip(edges, solutions):
            cnt[len(edge_solutions)].append(edge)
        if 0 in cnt:
            ERROR_MANAGER.addError('%s could not find any solutions for the edges %s'%\
                (self.feature.name, ', '.join(cnt[0])))

        for solution in product(*solutions):
            ins = {e: s.feature.outs[e] for e, s in izip(edges, solution)}
            outs = self.feature.getOutput(ins)

            resources = reduce(or_, (graph.resources for graph in solution), set())
            dependencies = {e: s.feature.name for e, s in izip(edges, solution)}
            feature_instance = self.feature(resources, dependencies, ins, outs)
            res = FeatureGraph(feature_instance)
            for e, s in izip(edges, solution):
                res.addEdge(e, feature_instance.name, s.feature.name)
                res.update(s)
            yield res

    def iterEdge(self, edge):
        for feature_name in self.graph.vs[self.feature.name][edge]:
            feature = self.graph.features[feature_name]
            if feature.name in self.visited:
                continue
            it = ResourceSolutionIterator(feature, self.resources)\
                if issubclass(feature.feature_class, Resource)\
                else SolutionIterator(feature, self.graph, self.resources, set(self.visited))
            for solution in it:
                yield solution

class ResourceSolutionIterator(object):
    def __init__(self, feature, resources):
        self.feature = feature
        self.c_hit = 0
        self.hits = self._getHits(feature, resources)

    def __str__(self):
        return self.feature.name

    def __iter__(self):
        if len(self.hits) == 0:
            ERROR_MANAGER.addError('%s does not match any provided resource'%\
                self.feature.name)
        for hit in self.hits:
            yield self._initFeatureGraph(hit)

    def _getHits(self, feature, resources):
        if issubclass(self.feature.feature_class, Target) and self.feature.feature_class.matches(resources['target']):
            return [resources['target']]
        return [resource for resource in resources.itervalues()\
            if resource.name != 'target' and self.feature.feature_class.matches(resource)]

    def _initFeatureGraph(self, resource):
        """ Create a single node FeatureGraph. """
        outs = self.feature.getOutput({'resource': resource})
        feature_instance = self.feature(set([resource]), {}, {}, outs)
        res = FeatureGraph(feature_instance)
        res.addResource(resource)
        return res
