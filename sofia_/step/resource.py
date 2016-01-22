from collections import OrderedDict
from step import Step
from sofia_.entity import Entity


class Resource(Step):
    """ A step that provides access to a disk based resource. """
    
    EXT = {}
    FORMAT = None

    def __init__(self, resources=None, dependencies=None, attr={}, ins=None, outs=None, converters={}, name=None):
        super(Resource, self).__init__(resources, dependencies, attr, ins, outs, converters, name)
        self.format = attr.get('name', self.FORMAT)
        self.interface = None

    def init(self):
        self.interface = self.get_interface(self.get_filename())

    def get_interface(self, filename):
        raise NotImplementedError()
    
    def calculate(self):
        """ Return the resource. """
        return self.interface
    
    def get_filename(self):
        """ Returns the filename of the resource. """
        return list(self.resources)[0].attr['filename']

    @classmethod
    def get_output(cls, ins={}, outs={}, attr={}, entity_graph=None):
        #TODO: Use entity_graph to properly construct out entities
        attr = ins['resource'].attr.copy() if len(ins) > 0 else {}
        return OrderedDict((out, Entity(out, attr=attr)) for out in outs)


class Target(Resource):
    """ The target resource that is to be annotated.
    
    This particular step should be used to provide iterative access to the
    entities stored in the resource.
    """
    def generate(self, entities, steps, entity_graph):
        """ Overridden from Action.generate to enforce use of reset to get the
        next entity. """
        if self.calculated:
            return
        outs = self.outs
        res = [self.calculate()] if len(outs) == 1 else self.calculate()
        self.calculated = True
        self.changed = False
        for out, entity in zip(outs, res):
            if out not in entities or entities[str(out)] is not entity:
                self.changed = True
            entities[str(out)] = entity

    def calculate(self):
        """ Get the next entity in the resource. """
        return self.interface.next()

    def _get_name(self, name=None):
        """ Overridden to return unique name. """
        return 'target'
