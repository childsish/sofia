from collections import defaultdict
from itertools import izip, product
from operator import or_

from sofia_.graph.action_graph import ActionGraph
from sofia_.converter import Converter
from sofia_.error_manager import ERROR_MANAGER
from entity_solution_iterator import EntitySolutionIterator


class StepSolutionIterator(object):
    def __init__(self, step, graph, provided_resources, workflow_template, maps={}, requested_resources=set(), visited=None):
        self.step = step
        self.graph = graph
        self.provided_resources = provided_resources
        self.maps = maps
        self.requested_resources = requested_resources
        self.workflow_template = workflow_template

        self.visited = set() if visited is None else visited
        self.visited.add(self.step.name)

    def __str__(self):
        return self.step.name
    
    def __iter__(self):
        original_entities = sorted(self.graph.get_children(self.step.name))
        equivalents = [self.graph.entity_graph.get_equivalent_descendents(entity) for entity in original_entities]
        resolvers = {entity: EntitySolutionIterator(entity,
                                                    self.graph,
                                                    self.provided_resources,
                                                    self.workflow_template,
                                                    self.maps,
                                                    self.requested_resources,
                                                    self.visited)
                     for entity in reduce(or_, equivalents)}
        resolvers = {entity: list(resolver) for entity, resolver in resolvers.iteritems()}

        res = defaultdict(list)
        for entities in product(*equivalents):
            disjoint_solutions = [resolvers[entity] for entity in entities]
            for disjoint_solution in product(*disjoint_solutions):
                ins = {o: s.action.outs[e] for o, e, s in izip(original_entities, entities, disjoint_solution)}

                converters = self.get_converters(ins)
                if converters is None:
                    continue

                for parent_entity, converter in converters.iteritems():
                    for entity, (fr, to) in converter.entities.iteritems():
                        ins[parent_entity].attr[entity] = to
                outs = self.step.get_output(ins, entity_graph=self.graph.entity_graph)
                if outs is None:
                    continue
                resources = reduce(or_, (graph.resources for graph in disjoint_solution), set())
                dependencies = {e: s.action.name for e, s in izip(original_entities, disjoint_solution)}
                action_instance = self.step(resources, dependencies, ins=ins, outs=outs, converters=converters)
                solution = ActionGraph(action_instance)
                for e, s in izip(original_entities, disjoint_solution):
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
        for error in errors:
            ERROR_MANAGER.add_error(error)

    def convert_edge_to(self, entity, entity_values, to_value, errors):
        converters = {}
        for fr_value, parent_entities in entity_values.iteritems():
            if fr_value == to_value:
                continue
            for parent_entity in parent_entities:
                path = [] if entity in self.graph.entity_graph.get_equivalent_descendents(parent_entity) else\
                    self.graph.entity_graph.get_descendent_path_to(parent_entity, entity)
                if path is None:
                    errors.add('Could not get {} from {} ({})'.format(entity, parent_entity, self.step.name))
                    return None
                if parent_entity not in converters:
                    converters[parent_entity] = Converter(entity, fr_value, to_value)
                converters[parent_entity].paths.append(path)
                converters[parent_entity].id_maps.append(self.maps[entity].make(fr_value, to_value))
        return converters
