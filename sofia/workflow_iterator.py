class WorkflowIterator(object):
    def __init__(self, workflow):
        self.workflow = workflow

    def next(self):
        return [head.next() for head in self.workflow.heads]
