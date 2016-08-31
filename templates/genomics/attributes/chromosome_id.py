from copy import copy
from functools import reduce
from operator import or_
from sofia.resolvers import AttributeResolver
from sofia.step import Converter, ConcreteStep
from sofia.workflow import StepNode, EntityNode


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'chromosome_id'

    def resolve_in(self, ins):
        ttl = 0
        for in_ in ins:
            in_ = in_.head.name
            ttl += 'chromosome_id' in self.entity_graph.entities[in_]['attributes'] or 'chromosome_id' in self.entity_graph.has_a.get_descendants(in_)
        if ttl < 2:
            return ins
        in_attributes = [in_.head.attributes[self.attribute] for in_ in ins]
        if len(reduce(or_, in_attributes)) < 2:
            return ins
        to = self.get_to(ins)

        res = []
        for in_ in ins:
            in_entity_type = in_.head
            out_entity_type = copy(in_entity_type)
            out_entity_type.attributes = copy(in_entity_type.attributes)
            out_entity_type.attributes[self.attribute] = {to}

            path = self.get_path(in_entity_type.name)
            if path is None:
                res.append(in_)
                continue
            fr = list(in_entity_type.attributes[self.attribute])[0]
            if fr == to:
                res.append(in_)
                continue

            name = 'Convert{}s{}To{}'.format(capitalise_name(in_entity_type.name), fr.capitalize(), to.capitalize())
            params = {
                 'map_file': self.id_maps['chromosome_id'],
                 'fr': fr,
                 'to': to,
                 'path': path
             }
            convert_step = ConcreteStep(Converter, name, [in_entity_type.name], [in_entity_type.name], params)
            out_attributes = copy(in_.head.attributes)
            out_attributes['chromosome_id'] = {to}
            step_node = StepNode(convert_step, {in_entity_type.name: out_attributes})
            step_node.add_entity_node(in_)

            in_ = EntityNode(out_entity_type)
            in_.add_step_node(step_node)
            res.append(in_)
        return res

    def get_to(self, ins):
        tos = reduce(or_, (in_.head.attributes[self.attribute] for in_ in ins if
                           'chromosome_id' not in self.entity_graph.has_a.get_descendants(in_.head.name)), set())
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


def capitalise_name(name):
    return ''.join(part.capitalize() for part in name.split('_')).replace('*', '')
