from lhc.graph import NPartiteGraph


class StepNode(NPartiteGraph):
    def __init__(self, step):
        super(StepNode, self).__init__(type(step).__name__)
        self.head = step
        self.add_vertex(step, 1)

    def add_entity_node(self, entity_node):
        self.update(entity_node)
        self.add_edge(entity_node.head, self.head)
