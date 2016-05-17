from collections import defaultdict
from copy import deepcopy
from itertools import izip, product
from operator import or_

from sofia.workflow.step_node import StepNode
from sofia.workflow.entity_node import EntityNode
from sofia.step.converter import Converter as ConverterStep
from sofia.converter import Converter
from sofia.error_manager import ERROR_MANAGER
from entity_resolver import EntityResolver


class StepResolver(object):
    def __init__(self, step, graph, provided_entities, workflow_template, maps={}, requested_entities=set(), visited=None):
        self.step = step
        self.graph = graph
        self.provided_entities = provided_entities
        self.maps = maps
        self.requested_entities = requested_entities
        self.workflow_template = workflow_template

        self.visited = set() if visited is None else visited
        self.visited.add(self.step.name)

    def __str__(self):
        return self.step.name

    def __hash__(self):
        return hash(str(self))
    
    def __iter__(self):
        entities = sorted(self.graph.get_children(self.step.name))
        resolvers = {entity: EntityResolver(entity,
                                            self.graph,
                                            self.provided_entities,
                                            self.workflow_template,
                                            self.maps,
                                            self.requested_entities,
                                            self.visited)
                                  for entity in entities}
        resolvers = {entity: list(resolver) for entity, resolver in resolvers.iteritems()}

        res = defaultdict(list)
        disjoint_solutions = [resolvers[entity] for entity in entities]
        for disjoint_solution in product(*disjoint_solutions):
            disjoint_solution = list(disjoint_solution)
            ins = {e: s.head for e, s in izip(entities, disjoint_solution)}

            converters = self.get_converters(ins)
            if converters is None:
                continue

            for i in xrange(len(entities)):
                entity = entities[i]
                if entity not in converters:
                    continue
                converter = converters[entity]
                s = disjoint_solution[i]
                s_ins = {entity: deepcopy(s.head)}
                s_outs = deepcopy(s_ins)
                for attribute, (fr, to) in converter.attributes.iteritems():
                    s_outs[entity].attributes[attribute] = to
                converter_step = ConverterStep(s.head.attributes['resource'], {entity: s.head.name}, ins=s_ins, outs=s_outs)
                converter_step.register_converter(converter)
                step_node = StepNode(converter_step)
                step_node.add_entity_node(disjoint_solution[i])
                entity_node = EntityNode(s_outs[entity])
                entity_node.add_step_node(step_node)
                disjoint_solution[i] = entity_node
            for entity, converter in converters.iteritems():
                for attribute, (fr, to) in converter.attributes.iteritems():
                    ins[entity].attributes[attribute] = {to}
            outs = self.step.get_output(ins, entity_graph=self.graph.entity_graph)
            if outs is None:
                continue
            resources = reduce(or_, (s.head.attributes['resource'] for s in disjoint_solution), set())  # TODO: make part of attribute resolution
            dependencies = {e: s.head.name for e, s in izip(entities, disjoint_solution)}
            step_instance = self.step(resources, dependencies, ins=ins, outs=outs)  # TODO: make part of attribute resolution
            solution = StepNode(step_instance)
            for s in disjoint_solution:
                solution.add_entity_node(s)
            res[len(resources - self.requested_entities)].append(solution)  # TODO: make part of attribute resolution
        if len(res) > 0:
            for solution in res[min(res)]:
                yield solution

    def get_converters(self, ins):
        matching_attributes = defaultdict(lambda: defaultdict(set))
        for edge, entity in ins.iteritems():
            for attribute_key, attribute_value in entity.attributes.iteritems():
                if attribute_key in {'resource', 'filename'}:
                    continue
                attribute_value = list(attribute_value)[0]
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
                        ERROR_MANAGER.add_error('Converter for {} can not convert {}'.format(attribute_key, value))
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