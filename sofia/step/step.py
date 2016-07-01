class Step(object):
    """
    A step that can be calculated from resources and other steps. Primarily concerned with execution of the step. Not
    concerned with attributes etc...
    """
    
    IN = []
    OUT = []
    PARAMS = []

    def __init__(self, **kwargs):
        """
        Make a copy of the input for the run function and consume the input to free up the queue for more input. If all
        input is consumed, there is no need to overload this function. Input is provided as lists. To copy and consume
        input the following commands can be run:

        1. To consume all the input
        >>> self.entity = input['entity'].splice()

        2. To consume one item from the input (and store it as a single item - not a list)
        >>> self.entity = input['entity'].pop()

        :param kwargs: input arguments
        """
        keys = kwargs.keys()
        values = self.splice(kwargs.values())
        for k, v in zip(keys, values):
            setattr(self, k, v)

    def run(self, **kwargs):
        """
        Run this step. The variable names are the entity names given in IN and OUT and are defined in the same order
        starting with IN and continuing with OUT. The entities are passed in streams with the functions 'peek' and 'pop'
        to get the entities from the input steams and 'push' to insert entities into the output streams. Run will be
        called until a StopIteration is pushed into all output streams

        :param kwargs: arguments defined in class IN and OUT members
        """
        raise NotImplementedError('a step has no implemented functionality')

    def finalise(self, **kwargs):
        """
        Finalise the step. This function creates output entities that can only be produced when it is known that the
        input stream has ended (eg. an output file). The variable names are the entity names given in OUT. The entities
        are passed in streams with the functions 'push' to insert entities into the output streams. Finalise will be
        called until a StopIteration is pushed into all output streams.

        :param kwargs: arguments defined in class OUT member
        """
        for value in kwargs.itervalues():
            value.push(StopIteration)

    def splice(self, *args):
        """
        Get the maximum number of entites from each stream, delete from the stream and return a copy of the deleted
        entities.

        :param args: input entities
        :return: copy of input entities
        """
        minimum = min(len(arg) for arg in args)
        res = [arg[:minimum] for arg in args]
        for arg in args:
            del arg[:minimum]
        return res

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
