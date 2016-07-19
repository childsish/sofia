class State(object):
    def __init__(self, step, outputs, index):
        self.step = step
        self.outputs = outputs
        self.index = index

    def run(self):
        self.step.run(**self.outputs)

    def finalise(self):
        self.step.finalise(**self.outputs)

    def is_stopped(self):
        return all(output.is_stopped() for output in self.outputs.itervalues())

    def get_user_warnings(self):
        return self.step.get_user_warnings()
