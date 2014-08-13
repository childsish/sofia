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
        #self.changed = self.needsUpdate(entities, features) #TODO: Take a closer look at self.changed
        if not self.changed:
            return entities[self.getName()]
        local_entities = {}
        for name, feature in self.dependencies.iteritems():
            if features[feature].changed:
                entities[feature] = features[feature].generate(entities, features)
                features[feature].changed = False
            local_entities[name] = entities[feature]
        #try:
        res = self.calculate(**local_entities)
        self.changed = True
        #except TypeError, e:
        #    raise TypeError(self.getName()  + ' ' + e.message.split(' ', 1)[1])
        return res
    
    def needsUpdate(self, entities, features):
        """Check if this features needs to be updated since the last iteration
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        if self.getName() not in entities:
            return True
        for dep in self.dependencies.itervalues():
            if features[dep].changed:
                return True
        return False

    def getName(self):
        if len(self.resources) == 0:
            return type(self).__name__
        return '%s:%s'%(type(self).__name__, ','.join(resource.name for resource in sorted(self.resources)))
