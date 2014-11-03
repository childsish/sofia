from feature_graph import FeatureGraph
from itertools import izip, repeat
from operator import or_

from ebias.features import Resource, Target
from ebias.error_manager import ERROR_MANAGER

class SolutionIterator(object):
    def __init__(self, feature, graph, provided_resources, visited=None, requested_attr=None):
        self.feature = feature
        self.graph = graph
        self.resources = provided_resources
        self.visited = set() if visited is None else visited
        self.edges = sorted(graph.vs[feature.name])
        self.edge_iterators = [iter(graph.vs[feature.name][edge]) for edge in self.edges]
        self.solution_iterators = len(self.edges) * [EmptySolutionIterator()]#[self._incrementDependency(i) for i in range(len(self.edges))]
        self.solutions = list(repeat(None, len(self.edges)))
        self.requested_attr = {} if requested_attr is None else requested_attr

        self.visited.add(self.feature.name)

    def __str__(self):
        return self.feature.name
    
    def __iter__(self):
        return self

    def next(self, requested_attr=None):
        solutions = self.solutions

        outs = None
        while outs is None:
            self._incrementEdge()
            ins = {e: s.feature.outs[e] for e, s in izip(self.edges, solutions)}
            outs = self.feature.getOutput(ins, requested_attr)
        
        resources = reduce(or_, (graph.resources for graph in solutions))
        dependencies = {e: s.feature.name for e, s in izip(self.edges, solutions)}
        feature_instance = self.feature(resources, dependencies, ins, outs)
        res = FeatureGraph(feature_instance)
        for e, s in izip(self.edges, solutions):
            res.addEdge(e, feature_instance.name, s.feature.name)
            res.update(s)
        return res

    def _incrementEdge(self, i=0):
        """ Increments the solutions of one edge """
        if i == len(self.edges):
            raise StopIteration()
        requested_attr = {}
        for j in xrange(i + 1, len(self.edges)):
            if self.solutions[j] is None:
                self._incrementEdge(j)
            requested_attr.update(self.solutions[j].feature.outs[self.edges[j]].attr)
        while True:
            try:
                self.solutions[i] = self.solution_iterators[i].next(requested_attr)
                break
            except StopIteration:
                while True:
                    try:
                        self.solution_iterators[i] = self._incrementDependency(i)
                        break
                    except StopIteration:
                        self._incrementEdge(i + 1)
                        self.edge_iterators[i] = iter(self.graph.vs[self.feature.feature_class.__name__][self.edges[i]])

    def _incrementDependency(self, i):
        """ Increments the dependencies of one edge """
        feature_name = None
        while feature_name is None:
            next = self.edge_iterators[i].next()
            if next not in self.visited:
                feature_name = next
        feature = self.graph.features[feature_name]
        return ResourceSolutionIterator(feature, self.resources)\
            if issubclass(feature.feature_class, Resource)\
            else SolutionIterator(feature, self.graph, self.resources, set(self.visited))

class ResourceSolutionIterator(object):
    def __init__(self, feature, resources):
        self.feature = feature
        self.c_hit = 0
        self.hits = self._getHits(feature, resources)

    def __str__(self):
        return self.feature.name

    def __iter__(self):
        return self

    def next(self, requested_attr=None):
        if len(self.hits) == 0:
            ERROR_MANAGER.addError('%s does not match any provided resource'%\
                self.feature.name)
        if self.c_hit == len(self.hits):
            raise StopIteration()
        self.c_hit += 1
        return self._initFeatureGraph(self.hits[self.c_hit - 1])

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

class EmptySolutionIterator(object):
    def next(self, requested_attr=None):
        raise StopIteration()
