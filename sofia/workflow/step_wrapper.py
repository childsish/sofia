class StepWrapper(object):
    def __init__(self, step):
        self.step = step
        self.ins = []
        self.outs = []

    def __str__(self):
        return str(self.step)

    def init(self):
        self.step.init()

    def run(self, **kwargs):
        res = self.step.run(**kwargs)
        if len(self.outs) == 1:
            return [res]
        return [[value] for value in res]
