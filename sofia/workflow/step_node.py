from lhc.graph import NPartiteGraph
from sofia.workflow_template import Template


class StepNode(NPartiteGraph):
    def __init__(self, step, out_attributes):
        super(StepNode, self).__init__(type(step).__name__)

        self.head = step
        self.add_vertex(step, Template.STEP_PARTITION)
        self.out_attributes = out_attributes

    def add_entity_node(self, entity_node):
        self.update(entity_node)
        self.add_edge(entity_node.head, self.head)
