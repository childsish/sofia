from modules.feature import Feature

class Resource(Feature):
    
    NAME = 'resource'
    RESOURCES = ['name']
    
    def __init__(self, resource_map, resources):
        super(Resource, self).__init__(resource_map, resources)
        self.resource = resources[self.name]
    
    @classmethod
    def _resolve(cls, resource_map):
        return resource_map['name']
    
class DynamicResource(Resource):
    def calculate(self, entities):
        return self.resource[entities['target']]

class StaticResource(Resource):
    def calculate(self, entities):
        return self.resource
