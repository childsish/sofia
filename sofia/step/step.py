class Step(object):
    """
    A step that can be calculated from resources and other steps. Primarily concerned with execution of the step. Not
    concerned with attributes etc...
    """
    
    IN = []
    OUT = []
    PARAMS = []

    def run(self, **kwargs):
        """
        Run this step

        Assumes dependencies are already resolved. This function must be
        overridden when implementing new steps.

        :param kwargs: arguments defined in class IN variable
        :return: output of running the step
        """
        return
        yield  # allows the generator to return nothing

    def finalise(self):
        return
        yield  # allows the generator to return nothing

    @classmethod
    def get_in_resolvers(cls):
        return {}

    @classmethod
    def get_out_resolvers(cls):
        return {}
    
    def __str__(self):
        """ Return the name of the step based on it's resources and
        arguments. """
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(str(self))

    def get_user_warnings(self):
        """ Called at the end to gather warnings for the user related to execution of the step.

        :return: set of warnings
        """
        return frozenset()
