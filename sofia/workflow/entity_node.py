from lhc.graph import NPartiteGraph


class EntityNode(NPartiteGraph):

    ENTITY_PARTITION = 0
    STEP_PARTITION = 1

    def __init__(self, entity):
        super(EntityNode, self).__init__(entity.alias)
        self.head = entity
        self.add_vertex(entity, self.ENTITY_PARTITION)

    def add_step_node(self, node):
        self.update(node)
        self.add_edge(node.head, self.head)
        node.head.outs.append(self.head)
