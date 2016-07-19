class StepWrapper(object):
    """
    A step wrapper allows steps to be connected by attributed entities, a critical part of creating workflows.
    """
    def __init__(self, step):
        self.ins = []
        self.outs = []

        self.step = step

    @property
    def name(self):
        return self.step.name

    def __str__(self):
        return str(self.step)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def init(self, input):
        return self.step.init(input)
