class EndOfStream(object):
    __slots__ = []


class NullEntity(object):
    __slots__ = []


class Step(object):
    """
    A step that can be calculated from resources and other steps. Primarily concerned with execution of the step. Not
    concerned with attributes etc... When implementing a step, please import:
    >>> from sofia.step import Step, EndOfStream, NullEntity
    """
    
    IN = []
    OUT = []
    PARAMS = []

    def run(self, ins, outs):
        """
        Run the step. This function must be overloaded to provide specific functionality.
        Input streams are accessed from the ins variable as members (eg. ins.entity). Input streams have the following
        fuctionality:

        1. If the input streams are synchronised, you can get all the next entities with:
        >>> entities = ins.pop()

        2. If the input streams are synchronised, you can get the number of entities in the stream with:
        >>> len(ins)

        3. Entities from individual streams can be accessed with:
        >>> ins.entity.pop()
        >>> len(ins.entity)
         where 'entity' is the name of the entity stream you want to pop from.

        Output streams are accessed from the outs variable as members (eg. out.entity). Output streams have the
        following functionality:

        1. To push an entity to an output stream:
        >>> outs.entity.push()
         where 'entity' is the entity stream you want to push to.

        2. To end a stream:
        >>> outs.entity.push(EndOfStream)

        :param ins: input streams. Individual streams can be accessed as members (ie. ins.entity)
        :param outs: output streams. Individual streams can be accessed as members (ie. outs.entity)
        :return: False if the step can still provide output, True if the step is done.
        """
        raise NotImplementedError('a step has no implemented functionality')

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
