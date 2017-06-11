class ConcreteStep(object):
    """
    A concrete step acts as the interface between user-defined steps and the template building engine. It can also be
    subclassed to create dynamically specialised steps. A concrete step has three main roles.
     1) Wrap a user-defined step so the IN and OUT class members are available to the template factory as .ins and .outs
        when making the template.
     2) Wrap the output of a user-defined step in a tuple.
     3) Allow generic steps to be dynamically specialised like the extractors and converters.
    """
    def __init__(self, step_class, *, name=None, ins=None, outs=None, params=None):
        self.step = None

        self.step_class = step_class
        self.name = step_class.__name__ if name is None else name
        self.ins = step_class.IN if ins is None else ins
        self.outs = step_class.OUT if outs is None else outs
        self.params = {} if params is None else params

    def __str__(self):
        return self.name

    def init(self):
        """
        Instantiate and initialise the step.
        :return:
        """
        self.step = self.step_class(**self.params)

    def consume_input(self, input):
        return self.step.consume_input(input)

    def run(self, **kwargs):
        """
        Run the step and wrap the output in a named tuple.
        :param kwargs: keyword arguments for the step
        :return: named tuple of output entities
        """
        return self.step.run(**kwargs)

    def finalise(self):
        return self.step.finalise()

    def get_user_warnings(self):
        return self.step.get_user_warnings()
