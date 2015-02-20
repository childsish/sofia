from collections import defaultdict
from itertools import izip, product
from operator import or_

from sofia_.graph.action_graph import ActionGraph
from sofia_.converter import Converter
from sofia_.error_manager import ERROR_MANAGER
from entity_solution_iterator import EntitySolutionIterator


class ActionSolutionIterator(object):
    def __init__(self, action, graph, provided_resources, workflow_template, maps={}, requested_resources=set(), visited=None):
        self.action = action
        self.graph = graph
        self.provided_resources = provided_resources
        self.maps = maps
        self.requested_resources = requested_resources
        self.workflow_template = workflow_template

        self.visited = set() if visited is None else visited
        self.visited.add(self.action.name)

    def __str__(self):
        return self.action.name
    
    def __iter__(self):
        entities = sorted(self.graph.get_children(self.action.name))
        resolvers = [EntitySolutionIterator(entity,
                                            self.graph,
                                            self.provided_resources,
                                            self.workflow_template,
                                            self.maps,
                                            self.requested_resources,
                                            self.visited)
                     for entity in entities]
        disjoint_solutions = [list(resolver) for resolver in resolvers]

        res = defaultdict(list)
        for disjoint_solution in product(*disjoint_solutions):
            ins = {e: s.action.outs[e] for e, s in izip(entities, disjoint_solution)}
            outs = self.action.get_output(ins)

            converters = self.get_converters(ins)
            if converters is None:
                continue

            resources = reduce(or_, (graph.resources for graph in disjoint_solution), set())
            dependencies = {e: s.action.name for e, s in izip(entities, disjoint_solution)}
            action_instance = self.action(resources, dependencies, ins=ins, outs=outs, converters=converters)
            solution = ActionGraph(action_instance)
            for e, s in izip(entities, disjoint_solution):
                solution.add_edge(e, action_instance.name, s.action.name)
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
                ERROR_MANAGER.add_error('There are no converters for {}'.format(entity_name))
                return None
            else:
                for value in entity_values:
                    if value not in self.maps[entity_name].hdrs:
                        ERROR_MANAGER.add_error('Converter for {} has can not convert {}'.format(entity_name, value))
                        return None

            edge_converters = self.convert_edge(entity_name, entity_values)
            if edge_converters is None:
                return None
            for edge, converter in edge_converters.iteritems():
                converters[edge].update(converter)
        return converters

    def convert_edge(self, entity, entity_values):
        errors = set()
        for to_value in entity_values:
            converters = self.convert_edge_to(entity, entity_values, to_value, errors)
            if converters is not None:
                return converters
        ERROR_MANAGER.add_error(str(errors))

    def convert_edge_to(self, entity, entity_values, to_value, errors):
        converters = defaultdict(Converter)
        for fr_value, edges in entity_values.iteritems():
            if fr_value == to_value:
                continue
            for edge in edges:
                path = self.graph.entity_graph.get_descendent_path_to(edge, entity)
                if path is None:
                    errors.add((edge, entity))
                    return None
                converters[edge].path.append(path)
                converters[edge].id_map.append(self.maps[entity].make(fr_value, to_value))
        return converters
