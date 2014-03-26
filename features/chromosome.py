from modules.feature import Feature

class Chromosome(Feature):
    
    NAME = 'chr'
    RESOURCES = ['target']
    DEPENDENCIES = [
        {'name': 'target',
         'feature': Target,
         'resource_map': {'name': 'seq'}
        }
    ]
    
    def calculate(self, target):
        return target.chr
