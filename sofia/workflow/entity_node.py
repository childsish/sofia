from lhc.graph import NPartiteGraph


class EntityNode(NPartiteGraph):
    def __init__(self, entity):
        super(EntityNode, self).__init__(entity.alias)
        self.head = entity
        self.add_vertex(entity, 0)

    def add_step_node(self, step_node):
        self.update(step_node)
        self.add_edge(step_node.head, self.head)
