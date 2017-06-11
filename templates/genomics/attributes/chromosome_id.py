from copy import copy
from sofia.resolvers import AttributeResolver
from sofia.step import Converter, ConcreteStep
from sofia.workflow import StepNode, EntityNode


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'chromosome_id'

    def resolve_in(self, ins):
        ttl = 0
        for in_ in ins:
            in_ = in_.head.name
            ttl += self.ATTRIBUTE in self.entity_graph.entities[in_]['attributes'] or self.ATTRIBUTE in self.entity_graph.has_a.get_descendants(in_)
        if ttl < 2:
            return ins

        in_attributes = []
        for in_ in ins:
            try:
                in_attributes.append(in_.head.attributes[self.attribute])
            except KeyError:
                raise KeyError('{} does not have the "{}" attribute'.format(in_.name, self.attribute))

        in_attributes = [in_.head.attributes[self.attribute] for in_ in ins]
        attributes = set()
        for attribute in in_attributes:
            attributes.update(attribute)
        if len(attributes) < 2:
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
            params = self.id_maps[self.ATTRIBUTE].copy()
            params['fr'] = fr
            params['to'] = to
            params['path'] = path

            convert_step = ConcreteStep(Converter, name=name, ins=[in_entity_type.name], outs=[in_entity_type.name], params=params)
            out_attributes = copy(in_.head.attributes)
            out_attributes[self.ATTRIBUTE] = {to}
            step_node = StepNode(convert_step, {in_entity_type.name: out_attributes})
            step_node.add_entity_node(in_)

            in_ = EntityNode(out_entity_type)
            in_.add_step_node(step_node)
            res.append(in_)
        return res

    def get_to(self, ins):
        """
        Resolve the output attribute value for 'chromosome_id'. Valid values are immutable, ie. the attribute key is not
        an actual entity. Mutable values will be changed to match the immutable value if unique. Otherwise an error is
        thrown.

        :param ins: iterable of input workflows
        :return: output attribute value
        """
        input_entities = set()
        attribute_values = set()
        for in_ in ins:
            if self.ATTRIBUTE not in self.entity_graph.has_a.get_descendants(in_.head.name):
                attribute_values.update(in_.head.attributes[self.ATTRIBUTE])
                input_entities.add(in_.head.name)
        if len(attribute_values) == 0:
            attribute_values = ins[0].head.attributes[self.ATTRIBUTE]
        elif len(attribute_values) > 1:
            raise ValueError('Unable to resolve single output attribute value for chromosome_id ({}),'.format(', '.join(attribute_values)))
        return list(attribute_values)[0]

    def get_path(self, entity):
        paths = self.entity_graph.get_descendent_paths(entity)
        for path in paths:
            if self.ATTRIBUTE in {step['name'] for step in path}:
                return path
        return None


def capitalise_name(name):
    return ''.join(part.capitalize() for part in name.split('_')).replace('*', '')
