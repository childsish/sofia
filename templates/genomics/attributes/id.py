from copy import copy
from operator import or_
from sofia.resolvers import AttributeResolver
from sofia.step import Convert
from sofia.converter import Converter
from sofia.workflow import StepNode, EntityNode


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'chromosome_id'

    def resolve_in(self, ins):
        if all('chromosome_id' not in self.entity_graph.has_a.get_descendents(in_.head.name) for in_ in ins):
            return ins
        in_attributes = [in_.head.attributes[self.attribute] for in_ in ins]
        if len(reduce(or_, in_attributes)) < 2:
            return ins
        to = self.get_to(ins)

        res = []
        for in_ in ins:
            entity_type = in_.head
            path = self.get_path(entity_type.name)
            if path is None:
                res.append(in_)
                continue
            fr = list(entity_type.attributes[self.attribute])[0]

            convert_step = Convert()
            convert_step.register_converter(Converter('chromosome_id', fr, to, path, self.id_maps['chromosome_id']))
            out_attributes = copy(in_.head.attributes)
            out_attributes['chromosome_id'] = {to}
            step_node = StepNode(convert_step, {entity_type.name: out_attributes})
            step_node.add_entity_node(in_)

            entity_type = copy(entity_type)
            entity_type.attributes = copy(entity_type.attributes)
            entity_type.attributes[self.attribute] = {to}

            in_ = EntityNode(entity_type)
            in_.add_step_node(step_node)
            res.append(in_)
        return res

    def get_to(self, ins):
        tos = reduce(or_, (in_.head.attributes[self.attribute] for in_ in ins
                           if 'chromosome_id' not in self.entity_graph.has_a.get_descendents(in_.head.name)), set())
        if len(tos) == 0:
            tos = ins[0].head.attributes[self.attribute]
        elif len(tos) > 1:
            raise ValueError('can not convert entities: {}'.format(', '.join(tos)))
        return list(tos)[0]

    def get_path(self, entity):
        paths = self.entity_graph.get_descendent_paths(entity)
        for path in paths:
            if 'chromosome_id' in {step['name'] for step in path}:
                return path
        return None