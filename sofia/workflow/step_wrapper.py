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
        return self.step.name

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def init(self):
        self.step.init()

    def run(self, inputs, n):
        keys = [in_.name for in_ in self.ins]
        inputs = self.step.consume_input(dict(zip(keys, inputs)))
        for output in self._loop_state(self.step.run(**inputs), n):
            yield output

    def finalise(self, n):
        for output in self._loop_state(self.step.finalise(), n):
            yield output

    def _loop_state(self, state, n):
        outputs = list(islice(state, n))
        while len(outputs) > 0:
            if len(self.step.outs) > 1:
                yield dict(zip(self.outs, outputs))
            else:
                yield {self.outs[0]: outputs}
            outputs = list(islice(state, n))

    def get_user_warnings(self):
        return self.step.get_user_warnings()
