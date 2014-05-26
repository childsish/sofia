from itertools import izip

class Feature(object):
    
    IN = []
    OUT = []
    
    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.changed = True
    
    def calculate(self, target, **kwargs):
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
            return entities[self.name]
        local_entities = {}
        for name, feature in self.dependencies.iteritems():
            entities[name] = features[feature].generate(entities, features)
            local_entities[name] = entities[name]
        res = self.calculate(**local_entities)
        return res
    
    def needsUpdate(self, entities, features):
        """Check if this features needs to be updated since the last iteration
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        if self.name not in entities:
            return True
        for dep in self.dependencies:
            if features[dep].changed:
                return True
        return False
