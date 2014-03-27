from modules.feature import Feature
from resource import DynamicResource

class Chromosome(Feature):
    
    NAME = 'chr'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        }
    ]
    
    def calculate(self, locus):
        return locus.chr
