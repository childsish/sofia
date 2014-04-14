from modules.feature import Feature

class Resource(Feature):
    """Biological information stored on the disk
    """
    
    NAME = 'resource'
    RESOURCES = ['name']
    
    def __init__(self, resource_map, resources):
        super(Resource, self).__init__(resource_map, resources)
        self.resource = resources[self.name]
    
    def _resolveName(self):
        return self.resource_map['name']

class Target(Resource):
    """The targetted feature
    """
    
    NAME = 'target'
    
    def calculate(self):
        return self.resource.next()
    
    def _resolveName(self):
        return 'target'

class StaticResource(Resource):
    """A resource that can be accessed by key
    """
    
    NAME = 'static_resource'
    
    def calculate(self):
        return self.resource
    
    def needsUpdate(self, entities, features):
        return self.name not in entities

class DynamicResource(Resource):
    """A resource that stays in step with the target
    """
    
    NAME = 'dynamic_resource'
    RESOURCES = ['name']
    DEPENDENCIES = [
        {'name': 'target',
         'feature': Target,
         'resource_map': {}
        }
    ]
    
    
    def __init__(self, resource_map, resources):
        super(DynamicResource, self).__init__(resource_map, resources)
        self.entity = None
    
    def calculate(self, target):
        return self.entity

    def needsUpdate(self, entities, features):
        if self.name == self.dependencies[0]:
            return False
        self.entity = self.resource[entities['target']]
        return self.name not in entities or self.entity is not entities[self.name]
