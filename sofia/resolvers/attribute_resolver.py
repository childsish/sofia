from operator import or_
from functools import reduce


class AttributeResolver(object):

    ATTRIBUTE = ''

    def __init__(self, attribute, entity_graph, step, id_maps):
        self.attribute = attribute
        self.entity_graph = entity_graph
        self.step = step
        self.id_maps = id_maps

    def resolve_in(self, ins):
        return ins

    def resolve_out(self, ins):
        values = reduce(or_, ins.values())
        return {
            entity: values for entity in self.step.outs
        }
