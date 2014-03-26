from modules.feature import Feature

class Position(Feature):
    
    NAME = 'pos'
    
    def calculate(self, target):
        return target.pos
