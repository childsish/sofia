class Target(Feature):
    
    NAME = 'target'
    RESOURCES = ['input']
    DEPENDENCIES = [
        {'name': 'input',
         'feature': StaticResource,
         'resource_map': {'name': 'input'}
        }
    ]
    
    def calculate(self, input):
        return input.next()
