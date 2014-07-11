from ebias.feature import Feature

class Resource(Feature):
    
    EXT = []
    TYPE = None
    PARSER = None
    
    def __init__(self, resource):
        self.resource = resource
    
    def init(self, **kwargs):
        self.parser = self.PARSER(self.resource.fname)
    
    def calculate(self):
        return self.parser
    
    def getName(self):
        return '%s:%s'%(type(self).__name__, self.resource.name)
    
    @classmethod
    def matches(cls, resource):
        return cls.matchesExtension(resource) and cls.matchesType(resource)
    
    @classmethod
    def matchesExtension(cls, resource):
        for ext in cls.EXT:
            if resource.fname.endswith(ext):
                return True
        return False
    
    @classmethod
    def matchesType(cls, resource):
        return cls.TYPE == resource.type
