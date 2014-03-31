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
    
    def calculate(self, target):
        if self.name == self.dependencies[0]:
            return target
        return self.resource[target]
