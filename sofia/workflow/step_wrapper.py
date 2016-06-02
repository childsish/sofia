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
        return self.step.run(**kwargs)
