class Feature(object):
    
    IN = []
    OUT = []
    
    def __init__(self, resources=None, dependencies=None):
        self.resources = set() if resources is None else resources
        self.dependencies = {} if dependencies is None else dependencies
        self.changed = True
    
    def __str__(self):
        return self.getName()
    
    def init(self):
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
        self.changed = self.needsUpdate(entities, features)
        if not self.changed:
            return entities[type(self).__name__]
        local_entities = {}
        for name, feature in self.dependencies.iteritems():
            entities[name] = features[feature].generate(entities, features)
            local_entities[name] = entities[name]
        #try:
        res = self.calculate(**local_entities)
        #except TypeError, e:
        #    raise TypeError(type(self).__name__  + ' ' + e.message.split(' ', 1)[1])
        return res
    
    def needsUpdate(self, entities, features):
        """Check if this features needs to be updated since the last iteration
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        if type(self).__name__ not in entities:
            return True
        for dep in self.dependencies:
            if features[dep].changed:
                return True
        return False

    def getName(self):
        if len(self.resources) == 0:
            return type(self).__name__
        return '%s:%s'%(type(self).__name__, ','.join(resource.name for resource in sorted(self.resources)))
