class StepWrapper(object):
    def __init__(self, step):
        self.step = step
        self.ins = []
        self.outs = []

    def __str__(self):
        return str(self.step)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def init(self):
        self.step.init()

    def run(self, **kwargs):
        res = self.step.run(**kwargs)
        if len(self.outs) == 1:
            return [res]
        return [[value] for value in res]

    def finalise(self):
        res = self.step.finalise()
        if len(self.outs) == 1:
            return [res]
        return [[value] for value in res]

    def get_user_warnings(self):
        return self.step.get_user_warnings()
