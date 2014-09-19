import sys

from error_manager import ERROR_MANAGER
from ebias.feature import Feature

class Resource(Feature):
    
    EXT = []
    TYPE = None
    PARSER = None
    
    def init(self):
        self.parser = self.PARSER(self.getFilename())
    
    def calculate(self):
        return self.parser
    
    def getName(self):
        return super(Resource, self).getName()
    
    def getFilename(self):
        return list(self.resources)[0].fname
    
    @classmethod
    def matches(cls, resource):
        match_ext = cls.matchesExtension(resource)
        match_type = cls.matchesType(resource)
        if match_ext and not match_type:
            ERROR_MANAGER.addError('%s matches extension but not type'%cls.__name__)
        elif match_type and not match_ext:
            ERROR_MANAGER.addError('%s matches type but not extension'%cls.__name__)
        return match_ext and match_type
    
    @classmethod
    def matchesExtension(cls, resource):
        for ext in cls.EXT:
            if resource.fname.endswith(ext):
                return True
        return False
    
    @classmethod
    def matchesType(cls, resource):
        return cls.TYPE == resource.type

class Target(Resource):
    def generate(self, entities, features):
        if self.calculated:
            return entities['target']
        entities['target'] = self.calculate()
        self.calculated = True
        self.changed = True
        return entities['target']

    def calculate(self):
        return self.parser.next()

    def getName(self):
        return 'target'

