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
        local_entities = {}
        for dep, DEP in izip(self.dependencies, self.DEPENDENCIES):
            if dep not in entities:
                print self.NAME
                entities[dep] = features[dep].generate(entities, features)
            local_entities[DEP['name']] = entities[dep]
        return self.calculate(**local_entities)
    
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
