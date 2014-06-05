from modules.feature import Feature

class Resource(Feature):
    
    PARSERS = {}
    
    def __init__(self, name, dependencies, fname):
        super(Resource, self).__init__(name, dependencies)
        self.fname = fname
        
        self.data = None
        for key in self.PARSERS.iterkeys():
            if fname.endswith(key):
                self.data = self.PARSERS[key](fname)
    
    def calculate(self):
        return self.data
    
    @classmethod
    def registerParser(cls, parser):
        cls.PARSERS[parser.EXT] = parser

class Target(Resource):
    
    def __iter__(self):
        return iter(self.data)
    
    def calculate(self):
        return self.data.next()
