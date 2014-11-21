from collections import defaultdict
from feature_graph import FeatureGraph
from itertools import izip, repeat, product
from operator import or_

from sofia.converter import Converter
from sofia.features import Resource, Target
from sofia.error_manager import ERROR_MANAGER

class SolutionIterator(object):
    def __init__(self, feature, graph, provided_resources, maps={}, visited=None):
        self.feature = feature
        self.graph = graph
        self.resources = provided_resources
        self.visited = set() if visited is None else visited
        self.maps = maps

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

            converters = self.getConverters(ins)
            if converters is None:
                continue

            resources = reduce(or_, (graph.resources for graph in solution), set())
            dependencies = {e: s.feature.name for e, s in izip(edges, solution)}
            feature_instance = self.feature(resources, dependencies, ins=ins, outs=outs, converters=converters)
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
                else SolutionIterator(feature, self.graph, self.resources, self.maps, set(self.visited))
            for solution in it:
                yield solution

    def getConverters(self, ins):
        matching_entities = defaultdict(lambda: defaultdict(set))
        for edge, entity in ins.iteritems():
            for entity_name, entity_value in entity.attr.iteritems():
                matching_entities[entity_name][entity_value].add(edge)

        converters = defaultdict(Converter)
        for entity_name, entity_values in matching_entities.iteritems():
            if len(entity_values) == 1:
                continue
            elif entity_name not in self.maps:
                ERROR_MANAGER.addError('There are no converters for %s'%entity_name)
                return None
            else:
                for value in entity_values:
                    if value not in self.maps[entity_name].hdrs:
                        ERROR_MANAGER.addError('Converter for %s has can not convert %s'%(entity_name, value))
                        return None

            edge_converters = self.convertEdge(entity_name, entity_values)
            if edge_converters is None:
                return None
            for edge, converter in edge_converters.iteritems():
                converters[edge].update(converter)
        return converters

    def convertEdge(self, entity, entity_values):
        errors = set() #TODO: Use later
        for to_value in entity_values:
            converters = self.convertEdgeTo(entity, entity_values, to_value, errors)
            if converters is not None:
                return converters
        ERROR_MANAGER.addError(str(errors))

    def convertEdgeTo(self, entity, entity_values, to_value, errors):
        converters = defaultdict(Converter)
        for fr_value, edges in entity_values.iteritems():
            if fr_value == to_value:
                continue
            for edge in edges:
                path = self.graph.entity_graph.getDescendentPathTo(edge, entity)
                if path is None:
                    errors.add((edge, entity))
                    return None
                converters[edge].path.append(path)
                converters[edge].id_map.append(self.maps[entity].make(fr_value, to_value))
        return converters

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
