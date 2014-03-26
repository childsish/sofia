from itertools import izip

class Feature(object):
    
    NAME = 'blank'
    RESOURCES = []
    DEPENDENCIES = []
    
    def __init__(self, resource_map, resources=None):
        self.resource_map = resource_map
        self.name = self._resolve(resource_map)
        self.dependencies = []
        for dep in self.DEPENDENCIES:
            dep_map = {k:resource_map[v] for k,v in dep['resource_map'].iteritems()}
            self.dependencies.append(dep['feature']._resolve(dep_map))
    
    def generate(self, entities, features):
        """Generate a feature
        
        This function resolves all dependencies and then calculates the
        feature.
        
        :param dict entities: currently calculated entities
        :param features: available features
        :type features: dict of features
        """
        local_entities = {'target': entities['target']}
        for dep, DEP in izip(self.dependencies, self.DEPENDENCIES):
            if dep not in entities:
                entities[dep] = features[dep].generate(entities, features)
            local_entities[dep] = entities[DEP]
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
    
    @classmethod
    def _resolve(cls, resource_map):
        if len(cls.RESOURCES) == 0:
            return cls.NAME
        return '{name}:{res}'.format(
            name=cls.NAME,
            res=','.join(resource_map[res] for res in cls.RESOURCES)
        )
