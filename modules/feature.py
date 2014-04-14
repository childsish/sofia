from itertools import izip

class Feature(object):
    
    NAME = 'blank'
    RESOURCES = []
    DEPENDENCIES = []
    
    def __init__(self, resource_map, resources=None):
        self.resource_map = resource_map
        self.name = self._resolveName()
        self.dependencies = []
    
    def generate(self, entities, features):
        """Generate a feature
        
        This function resolves all dependencies and then calculates the
        feature.
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        if not self.needsUpdate(entities, features):
            return entities[self.name]
        local_entities = {}
        for dep, DEP in izip(self.dependencies, self.DEPENDENCIES):
            entities[dep] = features[dep].generate(entities, features)
            local_entities[DEP['name']] = entities[dep]
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
            if features[dep].needsUpdate(entities, features):
                return True
        return False
    
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

    def generateDependencies(self, resources=None):
        res = []
        for dep in self.DEPENDENCIES:
            resource_map = {k:self.resource_map[v]\
                for k,v in dep['resource_map'].iteritems()}
            res.append(dep['feature'](resource_map, resources))
        self.dependencies = [feature.name for feature in res]
        return res
    
    def _resolveName(self):
        if len(self.RESOURCES) == 0:
            return self.NAME
        return '{name}:{res}'.format(
            name=self.NAME,
            res=','.join(self.resource_map[res] for res in self.RESOURCES)
        )
