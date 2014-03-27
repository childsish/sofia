from modules.feature import Feature

class Resource(Feature):
    """Biological information stored on the disk
    """
    
    NAME = 'resource'
    RESOURCES = ['name']
    
    def __init__(self, resource_map, resources):
        super(Resource, self).__init__(resource_map, resources)
        self.resource = resources[self.name]
    
    @classmethod
    def _resolve(cls, resource_map):
        return resource_map['name']

class Target(Resource):
    """The targetted feature
    """
    
    NAME = 'target'
    
    def calculate(self):
        return self.resource.next()

class StaticResource(Resource):
    """A resource that can be accessed by key
    """
    
    NAME = 'static_resource'
    
    def calculate(self):
        return self.resource

class DynamicResource(Resource):
    """A resource that stays in step with the target
    """
    
    NAME = 'dynamic_resource'
    RESOURCES = ['target']
    DEPENDENCIES = [
        {'name': 'target',
         'feature': Target,
         'resource_map': {'name': 'name'}
        }
    ]
    
    def calculate(self, target):
        return self.resource[target]
