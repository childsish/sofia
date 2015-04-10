from step import Step
from sofia_.entity import Entity


class Resource(Step):
    """ A step that provides access to a disk based resource. """
    
    EXT = {}
    FORMAT = None
    
    def calculate(self):
        """ Return the resource. """
        return self.parser
    
    def get_filename(self):
        """ Returns the filename of the resource. """
        return list(self.resources)[0].fname
    
    @classmethod
    def matches(cls, resource):
        """ Check if a disk-based source matches this resource. """
        if resource.format is not None:
            return resource.format == cls.FORMAT
        return any(resource.fname.endswith(ext) for ext in cls.EXT)

    @classmethod
    def get_output(cls, ins={}, outs={}, attr={}, entity_graph=None):
        attr = ins['resource'].attr.copy() if len(ins) > 0 else {}
        return {out: Entity(out, attr) for out in outs}
        #return {out: ENTITY_FACTORY.makeEntity(out, provided_resource.attr) for out in cls.OUT}


class Target(Resource):
    """ The target resource that is to be annotated.
    
    This particular step should be used to provide iterative access to the
    entities stored in the resource.
    """
    def generate(self, entities, steps):
        """ Overridden from Action.generate to enforce use of reset to get the
        next entity. """
        if self.calculated:
            return entities['target']
        entities['target'] = self.calculate()
        self.calculated = True
        self.changed = True
        return entities['target']

    def calculate(self):
        """ Get the next entity in the resource. """
        return self.parser.next()

    def _get_name(self, name=None):
        """ Overridden to return unique name. """
        return 'target'

    @classmethod
    def matches_format(cls, resource):
        """ Match the entity type of the disk-based source to this resource. """
        return set(t + '_set' for t in cls.OUT) == resource.types
