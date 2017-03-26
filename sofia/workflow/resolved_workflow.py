from lhc.graph import NPartiteGraph
from sofia.workflow_template import Template


class ResolvedWorkflow(NPartiteGraph):
    def __init__(self, provided_entities):
        super().__init__('Workflow')
        self.heads = []
        self.provided_entities = provided_entities

    def init(self):
        """ Initialise all the steps in the graph. """
        for step in self.partitions[Template.STEP_PARTITION]:
            step.init()

    def add_entity_node(self, entity_node):
        self.update(entity_node)
        self.heads.append(entity_node.head)
