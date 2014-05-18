from modules.feature import Feature

class Resource(Feature):
    
    EXT = ''
    
    def __init__(self, name, fname):
        self.fname = fname
        self.in_ = self.IN[:]
        self.out = self.OUT[:]

class Target(Resource):
    
    def calculate(self):
        return self.data.next()
