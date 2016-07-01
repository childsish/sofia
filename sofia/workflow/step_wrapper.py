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

    def run(self, output):
        keys = [in_.name for in_ in self.ins]
        input = dict(zip(keys, input))
        kwargs.update((out.name, output[out]) for out in self.outs)
        self.step.run(**kwargs)

    def finalise(self, output):
        kwargs = {out.name: output[out] for out in self.outs}
        self.step.finalise(**kwargs)

    def get_user_warnings(self):
        return self.step.get_user_warnings()
