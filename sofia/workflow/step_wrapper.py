from itertools import islice


class StepWrapper(object):
    def __init__(self, step):
        self.state = None
        self.ins = []
        self.outs = []

        self.running = False
        self.finalised = False

        self.step = step

    def __str__(self):
        return str(self.step)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def init(self):
        self.step.init()

    def run(self, inputs, n=None):
        self.running = True

        in_keys = [in_.name for in_ in self.ins]

        outputs = []
        if len(self.outs) == 1:
            if n is None:
                for input in inputs:
                    outputs.extend(self.step.run(**dict(zip(in_keys, input))))
            else:
                for input in inputs:
                    state = self.step.run(**dict(zip(in_keys, input)))
                    outputs.extend(islice(state, n - len(outputs)))
                    while len(outputs) == n:
                        yield {self.outs[0]: outputs}
                        outputs = list(islice(state, n))
            if len(outputs) > 0:
                yield {self.outs[0]: outputs}
        else:
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
        self.finalised = True

        outputs = []
        if len(self.outs) == 1:
            if n is None:
                outputs.extend(self.step.finalise())
            else:
                state = self.step.finalise()
                outputs.extend(islice(state, n - len(outputs)))
                while len(outputs) == n:
                    yield {self.outs[0]: outputs}
                    outputs = list(islice(state, n))
            if len(outputs) > 0:
                yield {self.outs[0]: outputs}
        else:
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
