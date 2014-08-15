class Feature(object):
    
    IN = []
    OUT = []
    
    def __init__(self, resources=None, dependencies=None):
        self.changed = True
        self.resources = set() if resources is None else resources
        self.dependencies = {} if dependencies is None else dependencies
    
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
        for name, feature in self.dependencies.iteritems():
            entities[feature] = features[feature].generate(entities, features)
        
        dependencies_changed = any(features[feature].changed for feature in\
            self.dependencies.itervalues())
        name = self.getName()
        if not dependencies_changed and name in entities:
            return entities[name]
        
        local_entities = {}
        for name, feature in self.dependencies.iteritems():
            local_entities[name] = entities[feature]
        res = self.calculate(**local_entities)
        self.changed = not (name in entities and entities[name] is res)
        return res
    
    def getName(self):
        if len(self.resources) == 0:
            return type(self).__name__
        return '%s:%s'%(type(self).__name__,\
            ','.join(resource.name for resource in sorted(self.resources)))

