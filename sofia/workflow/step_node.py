from lhc.graph import NPartiteGraph
from sofia.workflow_template import Template
from sofia.workflow.step_wrapper import StepWrapper


class StepNode(NPartiteGraph):
    def __init__(self, step, out_attributes):
        super().__init__(step.name)
        self.head = StepWrapper(step)
        self.add_vertex(self.head, Template.STEP_PARTITION)
        self.out_attributes = out_attributes

    def add_entity_node(self, node):
        self.update(node)
        self.add_edge(node.head, self.head)
        self.head.ins.append(node.head)
