from ebias.feature import Feature

class Resource(Feature):
    
    PARSERS = {}
    
    def __init__(self, name, dependencies, parser):
        super(Resource, self).__init__(name, dependencies)
        self.parser = parser
    
    def calculate(self):
        return self.parser

class Target(Resource):
    
    def __iter__(self):
        return iter(self.data)
    
    def calculate(self):
        return self.data.next()
