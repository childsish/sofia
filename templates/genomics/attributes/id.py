from copy import copy
from operator import or_
from sofia.resolvers import AttributeResolver
from sofia.step import Converter, ConcreteStep
from sofia.workflow import StepNode, EntityNode


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'chromosome_id'

    def resolve_in(self, ins):
        if all('chromosome_id' not in self.entity_graph.has_a.get_descendants(in_.head.name) for in_ in ins):
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

            name = 'Convert{}To{}'.format(fr.capitalize(), to.capitalize())
            params = {
                 'entity': 'chromosome_id',
                 'fr': fr,
                 'to': to,
                 'path': path,
                 'id_map': self.id_maps['chromosome_id']
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
        tos = reduce(or_, (in_.head.attributes[self.attribute] for in_ in ins
                           if 'chromosome_id' not in self.entity_graph.has_a.get_descendants(in_.head.name)), set())
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
