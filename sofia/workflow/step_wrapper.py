from itertools import islice


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

    def init(self):
        self.step.init()

    def run(self, inputs, n=None):
        in_keys = [in_.name for in_ in self.ins]
        outputs = []
        if n is None:
            for input in inputs:
                outputs.extend(self.step.run(**dict(zip(in_keys, input))))
        else:
            for input in inputs:
                state = self.step.run(**dict(zip(in_keys, input)))
                outputs.extend(islice(state, n - len(outputs)))
                while len(outputs) == n:
                    yield dict(zip(self.outs, zip(*outputs)))
                    outputs = list(islice(state, n))
        if len(outputs) > 0:
            yield dict(zip(self.outs, zip(*outputs)))

    def finalise(self, n=None):
        outputs = []
        if n is None:
            outputs.extend(self.step.finalise())
        else:
            state = self.step.finalise()
            outputs.extend(islice(state, n - len(outputs)))
            while len(outputs) == n:
                yield dict(zip(self.outs, zip(*outputs)))
                outputs = list(islice(state, n))
        if len(outputs) > 0:
            yield dict(zip(self.outs, zip(*outputs)))

    def get_user_warnings(self):
        return self.step.get_user_warnings()
