class Step(object):
    """
    A step that can be calculated from resources and other steps. Primarily concerned with execution of the step. Not
    concerned with attributes etc...
    """
    
    IN = []
    OUT = []
    PARAMS = []

    def consume_input(self, input):
        """
        Make a copy of the input for the run function and consume the input to free up the queue for more input. If all
        input is consumed, there is no need to overload this function. Input is provided as lists. To copy and consume
        input the following commands can be run:

        1. To consume all the input
        >>> copy['entity'] = input['entity'][:]
        >>> del input['entity'][:]

        2. To consume one item from the input (and pass it to run as a single item - not a list)
        >>> copy['entity'] = input['entity'].pop()

        3. To use an item but not consume it
        >>> copy['entity'] = input['entity'][0]

        :param input: input arguments
        :return: copy of the input arguments
        """
        copy = {}
        for key in input:
            copy[key] = input[key][:]
            del input[key][:]
        return copy

    def run(self, **kwargs):
        """
        Run this step

        Assumes dependencies are already resolved. This function must be overridden when implementing new steps.

        :param kwargs: arguments defined in class IN variable
        :return: output of running the step
        """
        return
        yield  # allows the generator to return nothing

    def finalise(self):
        """
        Finalise the step. This function is a generator for the output entities that can only be produced when it is
        known that the input stream has ended (eg. an output file).
        :return:
        """
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
