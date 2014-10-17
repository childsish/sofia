from operator import and_
from ebias.entity import Entity

class Feature(object):
    """ A feature that can be calculated from resources and other features. """
    
    IN = []
    OUT = []
    
    def __init__(self, resources=None, dependencies=None, kwargs={}, outs=None):
        self.changed = True
        self.calculated = False
        self.resources = set() if resources is None else resources
        self.dependencies = {} if dependencies is None else dependencies
        self.kwargs = kwargs
        self.outs = {out: Entity() for out in self.OUT} if outs is None else outs
        self.name = self._getName()
    
    def __str__(self):
        """ Return the name of the feature based on it's resources and
        arguments. """
        return self.name
    
    def init(self):
        """ Initialise the feature.

        When overridden, this function can be passed arguments that are parsed
        from the command line.
        """
        pass
    
    def calculate(self, **kwargs):
        """Calculate this feature
        
        Assumes dependencies are already resolved. This function must be
        overridden when implementing new features.
        
        :param dict entities: currently calculated entities. The target is at
            entities['target'].
        """
        raise NotImplementedError('You must override this function')

    def format(self, entity):
        """Convert entity produced by this feature to a string
        
        :param object entity: convert this entity
        """
        return str(entity)
    
    def generate(self, entities, features):
        """Generate a feature
        
        This function resolves all dependencies and then calculates the
        feature.
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        name = self.name
        if self.calculated:
            return entities[name]
        
        dependencies_changed = False
        for feature in self.dependencies.itervalues():
            features[feature].generate(entities, features)
            if features[feature].changed:
                dependencies_changed = True
        if not dependencies_changed and name in entities:
            self.calculated = True
            self.changed = False
            return entities[name]
        
        local_entities = {}
        for dependency_name, feature in self.dependencies.iteritems():
            local_entities[dependency_name] = entities[feature]
        res = self.calculate(**local_entities)
        self.calculated = True
        self.changed = not (name in entities and entities[name] is res)
        entities[name] = res
        return res
    
    def reset(self, features):
        """ Resets the calculation status of this feature and all dependencies 
        to False.
        """
        self.calculated = False
        for feature in self.dependencies.itervalues():
            features[feature].reset(features)
    
    def _getName(self):
        """ Return the name of the feature based on it's resources and
        arguments. """
        name = [type(self).__name__]
        if len(self.resources) != 0:
            name.append(','.join(resource.name for resource in self.resources))
        if len(self.kwargs) != 0:
            name.append(','.join('%s=%s'%e for e in self.kwargs.iteritems()))
        return ':'.join(name)
    
    @classmethod
    def iterOutput(cls, ins={}, outs={}, attrs={}):
        """ Iterate through concrete output possibilities
        
        Attributes provided by the user and are interpreted as requested
        attributes. Attributes found in entities must be propogated.
        """
        #TODO use the entity graph to return proper entities with attributes
        # Check that input entity attributes match
        common_attr_names = reduce(and_, (set(entity.attrs) for entity in ins.itervalues()))
        for name in common_attr_names:
            attrs = set()
            for entity in ins.itervalues():
                attrs[name].add(entity.attrs[name])
            if len(attrs) > 1:
                raise StopIteration()
        
        # Yield the output entities
        attrs = {}
        for entity in ins.itervalues():
            attrs.update(entity.attrs)
        yield {out: Entity(attrs) for out in outs}
        #yield {out: ENTITY_FACTORY.makeEntity(out, attrs) for out in outs}
