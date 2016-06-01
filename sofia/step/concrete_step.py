class ConcreteStep(object):
    """
    A concrete step has two main roles. 1) Wrap a user-defined step so the IN and OUT class members are available to the template
    factory as .ins and .outs when making the template. 2) Allow custom steps to be created like the extractors and
    converters.
    """
    def __init__(self, step_class, name=None, ins=None, outs=None, params=None):
        self.step = None

        self.step_class = step_class
        self.name = step_class.__name__ if name is None else name
        self.ins = step_class.IN if ins is None else ins
        self.outs = step_class.OUT if outs is None else outs
        self.params = {} if params is None else params

    def __str__(self):
        return self.name

    def init(self):
        self.step = self.step_class(**self.params)

    def run(self, **kwargs):
        return self.step.run(**kwargs)
