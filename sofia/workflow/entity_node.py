from lhc.graph import NPartiteGraph
from sofia.workflow_template import Template


class EntityNode(NPartiteGraph):
    def __init__(self, entity):
        super().__init__(entity.alias)
        self.head = entity
        self.add_vertex(entity, Template.ENTITY_PARTITION)

    def add_step_node(self, node):
        self.update(node)
        self.add_edge(node.head, self.head)
        node.head.outs.append(self.head)
