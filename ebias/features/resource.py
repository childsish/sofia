from feature import Feature
from ebias.entity import Entity
from ebias.error_manager import ERROR_MANAGER

class Resource(Feature):
    """ A feature that provides access to a disk based resource. """
    
    EXT = []
    PARSER = None
    
    def init(self):
        """ Initialise the resource using the given parser.
        
        This function can be overridden to accept arguments and customise
        resource initialisation.
        """
        self.parser = self.PARSER(self.getFilename())
        self.name = super(Resource, self)._getName()
    
    def calculate(self):
        """ Return the resource. """
        return self.parser
    
    def getFilename(self):
        """ Returns the filename of the resource. """
        return list(self.resources)[0].fname
    
    @classmethod
    def matches(cls, resource):
        """ Check if a disk-based source matches this resource. """
        match_ext = cls.matchesExtension(resource)
        match_type = cls.matchesType(resource)
        if match_ext and not match_type:
            ERROR_MANAGER.addError('%s matches extension but not type'%cls.__name__)
        elif match_type and not match_ext:
            ERROR_MANAGER.addError('%s matches type but not extension'%cls.__name__)
        return match_ext and match_type
    
    @classmethod
    def matchesExtension(cls, resource):
        """ Match the extension of the disk-based source to this resource. """
        for ext in cls.EXT:
            if resource.fname.endswith(ext):
                return True
        return False
    
    @classmethod
    def matchesType(cls, resource):
        """ Match the entity type of the disk-based source to this resource. """
        return tuple(cls.OUT) == resource.type

    @classmethod
    def iterOutput(cls, provided_resource):
        attr = provided_resource.attr
        yield {out: Entity(out, attr) for out in cls.OUT}
        #yield {out: ENTITY_FACTORY.makeEntity(out, provided_resource.attr) for out in cls.OUT}

class Target(Resource):
    """ The target resource that is to be annotated.
    
    This particular feature should be used to provide iterative access to the
    entities stored in the resource.
    """
    def generate(self, entities, features):
        """ Overridden from Feature.generate to enforce use of reset to get the
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

    def _getName(self):
        """ Overridden to return unique name. """
        return 'target'

    @classmethod
    def matchesType(cls, resource):
        """ Match the entity type of the disk-based source to this resource. """
        return tuple(t + '_set' for t in cls.OUT) == resource.type
