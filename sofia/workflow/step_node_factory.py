from itertools import izip, repeat
from operator import or_
from step_node import StepNode


class StepNodeFactory(object):
    def __init__(self, step, attributes):
        self.step = step
        self.attributes = attributes
        self.in_resolvers = {attribute.ATTRIBUTE: attribute.resolve_in for attribute in self.attributes}
        for attribute, resolver in step.step_class.get_in_resolvers().iteritems():
            self.in_resolvers[attribute] = resolver
        self.out_resolvers = {attribute.ATTRIBUTE: attribute.resolve_out for attribute in self.attributes}
        for attribute, resolver in step.step_class.get_out_resolvers().iteritems():
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
        attributes = reduce(or_, (set(entity_node.head.attributes) for entity_node in entity_nodes))
        for attribute in attributes:
            if attribute in self.in_resolvers:
                entity_nodes = self.in_resolvers[attribute](entity_nodes)
        return entity_nodes

    def resolve_outs(self, entity_nodes):
        attributes = reduce(or_, (set(entity_node.head.attributes) for entity_node in entity_nodes), set())
        outs = {}
        for attribute in attributes:
            in_values = {entity_node.head.name: (entity_node.head.attributes[attribute] if attribute in entity_node.head.attributes else set()) for entity_node in entity_nodes}

            if attribute not in self.out_resolvers:
                value = reduce(or_, in_values.itervalues())
                partial_outs = dict(izip(self.step.outs, repeat(value, len(self.step.outs))))
            else:
                partial_outs = self.out_resolvers[attribute](in_values)

            for entity, value in partial_outs.iteritems():
                if len(value) == 0:
                    continue
                if entity not in outs:
                    outs[entity] = {}
                outs[entity][attribute] = value
        return outs
