from collections import defaultdict
from copy import deepcopy
from itertools import izip, product
from operator import or_

from sofia_.graph import Workflow
from sofia_.step.converter import Converter as ConverterStep
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
        entities = sorted(self.graph.get_children(self.step.name))
        resolvers = {entity: EntitySolutionIterator(entity,
                                                    self.graph,
                                                    self.provided_resources,
                                                    self.workflow_template,
                                                    self.maps,
                                                    self.requested_resources,
                                                    self.visited)
                                  for entity in entities}
        resolvers = {entity: list(resolver) for entity, resolver in resolvers.iteritems()}

        res = defaultdict(list)
        disjoint_solutions = [resolvers[entity] for entity in entities]
        for disjoint_solution in product(*disjoint_solutions):
            disjoint_solution = list(disjoint_solution)
            ins = {e: deepcopy(s.step.outs[e]) for e, s in izip(entities, disjoint_solution)}

            converters = self.get_converters(ins)
            if converters is None:
                continue

            for i in xrange(len(entities)):
                entity = entities[i]
                if entity not in converters:
                    continue
                converter = converters[entity]
                s = disjoint_solution[i]
                s_ins = {entity: deepcopy(s.step.outs[entity])}
                s_outs = deepcopy(s_ins)
                for attribute, (fr, to) in converter.attributes.iteritems():
                    s_outs[entity].attr[attribute] = to
                converter_step = ConverterStep(s.resources, {entity: s.step.name}, ins=s_ins, outs=s_outs)
                converter_step.register_converter(converter)
                step = Workflow(converter_step)
                step.join(disjoint_solution[i], s_ins[entity])
                disjoint_solution[i] = step
            for entity, converter in converters.iteritems():
                for attribute, (fr, to) in converter.attributes.iteritems():
                    ins[entity].attr[attribute] = to
            outs = self.step.get_output(ins, entity_graph=self.graph.entity_graph)
            if outs is None:
                continue
            resources = reduce(or_, (graph.resources for graph in disjoint_solution), set())
            dependencies = {e: s.step.name for e, s in izip(entities, disjoint_solution)}
            step_instance = self.step(resources, dependencies, ins=ins, outs=outs)
            solution = Workflow(step_instance)
            for entity, s in izip(entities, disjoint_solution):
                solution.join(s, s.step.outs[entity])
            res[len(resources - self.requested_resources)].append(solution)
        if len(res) > 0:
            for solution in res[min(res)]:
                yield solution

    def get_converters(self, ins):
        matching_attributes = defaultdict(lambda: defaultdict(set))
        for edge, entity in ins.iteritems():
            for attribute_key, attribute_value in entity.attr.iteritems():
                if attribute_key in {'resource', 'filename'}:
                    continue
                matching_attributes[attribute_key][attribute_value].add(edge)

        converters = defaultdict(Converter)
        for attribute_key, attribute_values in matching_attributes.iteritems():
            if len(attribute_values) == 1:
                continue
            elif attribute_key not in self.maps:
                ERROR_MANAGER.add_error('There are no converters for attribute "{}"'.format(attribute_key))
                return None
            else:
                for value in attribute_values:
                    if value not in self.maps[attribute_key].hdrs:
                        ERROR_MANAGER.add_error('Converter for {} has can not convert {}'.format(attribute_key, value))
                        return None

            edge_converters = self.convert_edge(attribute_key, attribute_values)
            if edge_converters is None:
                return None
            for edge, converter in edge_converters.iteritems():
                converters[edge].update(converter)
        return converters

    def convert_edge(self, attribute_key, attribute_values):
        errors = set()
        for to_value in attribute_values:
            converters = self.convert_edge_to(attribute_key, attribute_values, to_value, errors)
            if converters is not None:
                return converters
        for error in errors:
            ERROR_MANAGER.add_error(error)

    def convert_edge_to(self, attribute_key, attribute_values, to_value, errors):
        converters = {}
        for fr_value, entities in attribute_values.iteritems():
            if fr_value == to_value:
                continue
            for entity in entities:
                path = [] if attribute_key in self.graph.entity_graph.get_equivalent_descendents(entity) else\
                    self.graph.entity_graph.get_descendent_path_to(entity, attribute_key)
                if path is None:
                    errors.add('Could not get {} from {} ({})'.format(attribute_key, entity, self.step.name))
                    return None
                if entity not in converters:
                    converters[entity] = Converter(attribute_key, fr_value, to_value)
                converters[entity].paths.append(path)
                converters[entity].id_maps.append(self.maps[attribute_key].make(fr_value, to_value))
        return converters
