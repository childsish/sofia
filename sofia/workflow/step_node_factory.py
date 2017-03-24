from itertools import repeat
from sofia.workflow.step_node import StepNode


class StepNodeFactory(object):
    def __init__(self, step, attributes):
        self.step = step
        self.attributes = attributes
        self.in_resolvers = {attribute.ATTRIBUTE: attribute.resolve_in for attribute in self.attributes}
        for attribute, resolver in step.step_class.get_in_resolvers().items():
            self.in_resolvers[attribute] = resolver
        self.out_resolvers = {attribute.ATTRIBUTE: attribute.resolve_out for attribute in self.attributes}
        for attribute, resolver in step.step_class.get_out_resolvers().items():
            self.out_resolvers[attribute] = resolver

    def __str__(self):
        return self.step.name

    def make(self, entity_nodes):
        entity_nodes = self.resolve_ins(entity_nodes)
        out_attributes = self.resolve_outs(entity_nodes)
        res = StepNode(self.step, out_attributes)
        for entity_node in entity_nodes:
            res.add_entity_node(entity_node)
        return res

    def resolve_ins(self, entity_nodes):
        attributes = self._merge_attributes(entity_nodes)
        for attribute in attributes:
            if attribute in self.in_resolvers:
                entity_nodes = self.in_resolvers[attribute](entity_nodes)
        return entity_nodes

    def resolve_outs(self, entity_nodes):
        attributes = self._merge_attributes(entity_nodes)

        outs = {}
        for attribute in attributes:
            in_values = {entity_node.head.name: (entity_node.head.attributes[attribute] if attribute in entity_node.head.attributes else set()) for entity_node in entity_nodes}

            if attribute not in self.out_resolvers:
                values = set()
                for value in in_values.values():
                    values.update(value)
                partial_outs = dict(zip(self.step.outs, repeat(values, len(self.step.outs))))
            else:
                partial_outs = self.out_resolvers[attribute](in_values)

            for entity, value in partial_outs.items():
                if len(value) == 0:
                    continue
                if entity not in outs:
                    outs[entity] = {}
                outs[entity][attribute] = value
        return outs

    def _merge_attributes(self, entity_nodes):
        attributes = set()
        for entity_node in entity_nodes:
            attributes.update(set(entity_node.head.attributes))
        return attributes
