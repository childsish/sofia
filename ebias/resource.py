from ebias.feature import Feature

class Resource(Feature):
    
    EXT = []
    TYPE = None
    PARSER = None
    TARGET = False
    
    def init(self, **kwargs):
        self.parser = self.PARSER(self.getFilename())
    
    def calculate(self):
        return self.parser
    
    def getName(self):
        return 'target' if self.TARGET else super(Resource, self).getName()
    
    def getFilename(self):
        return list(self.resources)[0].fname
    
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

