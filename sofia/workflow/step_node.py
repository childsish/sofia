from lhc.graph import NPartiteGraph
from .step_wrapper import StepWrapper


class StepNode(NPartiteGraph):

    ENTITY_PARTITION = 0
    STEP_PARTITION = 1

    def __init__(self, step, out_attributes):
        super(StepNode, self).__init__(step.name)
        self.head = StepWrapper(step)
        self.add_vertex(self.head, self.STEP_PARTITION)
        self.out_attributes = out_attributes

    def add_entity_node(self, node):
        self.update(node)
        self.add_edge(node.head, self.head)
        self.head.ins.append(node.head)
