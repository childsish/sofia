from collections import defaultdict
from itertools import izip, product

from operator import or_

from sofia_.graph.action_graph import ActionGraph
from sofia_.converter import Converter
from sofia_.action import Resource, Target
from sofia_.error_manager import ERROR_MANAGER
from sofia_.parser.provided_resource import ProvidedResource


class EntitySolutionIterator(object):
    def __init__(self, entity, graph, provided_resources, maps={}, requested_resources=set(), visited=None):
        self.entity = entity
        self.graph = graph
        self.resources = provided_resources
        self.maps = maps
        self.requested_resources = requested_resources

        self.visited = set() if visited is None else visited
        self.visited.add(self.action.name)

    def __str__(self):
        return self.action.name
    
    def __iter__(self):
        for solution in self.iter_action_solutions():
            yield solution

    def iter_entity_solutions(self):
        for action_name in self.graph.es[self.entity]:
            if action_name in self.visited:
                continue
            action = self.graph.actions[action_name]
            it = ResourceSolutionIterator(action, self.resources)\
                if issubclass(action.action_class, Resource)\
                else self.iter_action_solutions(action)
            for solution in it:
                yield solution

    def iter_action_solutions(self, action):
        entities = sorted(self.graph.vs[action.name])
        disjoint_solutions = [list(EntitySolutionIterator(entity, self.graph, self.resources, self.maps,
                                                          self.requested_resources, set(self.visited)))
                              for entity in entities]

        res = defaultdict(list)
        for disjoint_solution in product(*disjoint_solutions):
            ins = {e: s.action.outs[e] for e, s in izip(entities, disjoint_solution)}
            outs = self.action.getOutput(ins)

            converters = self.get_converters(ins)
            if converters is None:
                continue

            resources = reduce(or_, (graph.resources for graph in disjoint_solution), set())
            dependencies = {e: s.action.name for e, s in izip(entities, disjoint_solution)}
            action_instance = self.action(resources, dependencies, ins=ins, outs=outs, converters=converters)
            solution = ActionGraph(action_instance)
            for e, s in izip(entities, disjoint_solution):
                solution.addEdge(e, action_instance.name, s.action.name)
                solution.update(s)
            res[len(resources - self.requested_resources)].append(solution)
        if len(res) > 0:
            for solution in res[min(res)]:
                yield solution

    def get_converters(self, ins):
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

            edge_converters = self.convert_edge(entity_name, entity_values)
            if edge_converters is None:
                return None
            for edge, converter in edge_converters.iteritems():
                converters[edge].update(converter)
        return converters

    def convert_edge(self, entity, entity_values):
        errors = set() #TODO: Use later
        for to_value in entity_values:
            converters = self.convert_edge_to(entity, entity_values, to_value, errors)
            if converters is not None:
                return converters
        ERROR_MANAGER.addError(str(errors))

    def convert_edge_to(self, entity, entity_values, to_value, errors):
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
    def __init__(self, action, resources):
        self.action = action
        self.c_hit = 0
        self.hits = self._get_hits(action.action_class, resources)

    def __str__(self):
        return self.action.name

    def __iter__(self):
        if len(self.hits) == 0:
            ERROR_MANAGER.addError('%s does not match any provided resource' %
                                   self.action.name)
        for hit in self.hits:
            yield self._init_action_graph(hit)

    def _get_hits(self, action, resources):
        if issubclass(action, Target) and action.matches(resources['target']):
            return [resources['target']]
        res = [resource for resource in resources.itervalues()
               if resource.name != 'target' and action.matches(resource)]
        if hasattr(action, 'DEFAULT'):
            import os
            import sys

            fname = action.DEFAULT
            full_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'data', fname)
            res.append(ProvidedResource(full_path, action.OUT[0]))
        return res

    def _init_action_graph(self, resource):
        """ Create a single node ActionGraph. """
        outs = self.action.getOutput({'resource': resource})
        action_instance = self.action(set([resource]), {}, {}, outs)
        res = ActionGraph(action_instance)
        res.addResource(resource)
        return res
