from lhc.graph import NPartiteGraph


class ResolvedWorkflow(NPartiteGraph):
    def __init__(self):
        super(ResolvedWorkflow, self).__init__('Workflow')
        self.heads = []

    def init(self):
        """ Initialise all the steps in the graph. """
        for step in self.partitions[1]:
            params = {key: step.attr[key] for key in step.PARAMS if key in step.attr}
            step.init(**params)

    def add_entity_node(self, entity_node):
        self.update(entity_node)
        self.heads.append(entity_node.head)
