from modules.feature import Feature
from resource import DynamicResource

class Gene(Feature):
    
    NAME = 'chr_mut'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        }
    ]
    
    def calculate(self, locus):
        return '%s%s%s'%(locus.ref, locus.pos, locus.alt)
