from collections import OrderedDict
from sofia.entity_type import EntityType


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
        raise NotImplementedError('You must override this function')

    @classmethod
    def get_in_resolvers(cls):
        return {}

    @classmethod
    def get_out_resolvers(cls):
        return {}
    
    def __init__(self, resources=None, dependencies=None, attr={}, ins=None, outs=None, name=None):
        # TODO: Consider equivalence of dependencies and ins
        self.resources = set() if resources is None else resources
        self.dependencies = {} if dependencies is None else dependencies
        self.attr = attr
        self.ins = OrderedDict([(in_, EntityType(in_)) for in_ in self.IN]) if ins is None else ins
        self.outs = OrderedDict([(out, EntityType(out)) for out in self.OUT]) if outs is None else outs
        self.name = self._get_name(name)
    
    def __str__(self):
        """ Return the name of the step based on it's resources and
        arguments. """
        return self.name

    def __repr__(self):
        return type(self).__name__

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(str(self))

    def init(self):
        """ Initialise the step.

        When overridden, this function can be passed arguments that are parsed
        from the command line.
        """
        pass

    def get_attributes(self):
        res = {}
        for out in self.outs.itervalues():
            res.update(out.attr)
        return res

    def get_user_warnings(self):
        """ Called at the end to gather warnings for the user related to execution of the step.

        :return: set of warnings
        """
        return frozenset()

    def _get_name(self, name=None):
        """ Return the name of the step based on it's resources and arguments. """
        res = [type(self).__name__ if name is None else name]
        attributes = OrderedDict()
        for out in self.outs.itervalues():
            attributes.update(out.attributes)
        for key, value in attributes.iteritems():
            res.append('{}={}'.format(key, ','.join(value)))
        return '\n'.join(res)
