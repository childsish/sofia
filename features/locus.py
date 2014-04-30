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

class Position(Feature):
    
    NAME = 'pos'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        }
    ]
    
    def calculate(self, locus):
        if hasattr(locus, 'pos'):
            return locus.pos + 1
        elif hasattr(locus, 'start'):
            return locus.start + 1
        msg = 'Can not extract position feature from type: {type}'
        raise TypeError(msg.format(type=type(locus)))

class Quality(Feature):
    
    NAME = 'qual'
    RESOURCES = ['locus']
    DEPENDENCIES = [
        {'name': 'locus',
         'feature': DynamicResource,
         'resource_map': {'name': 'locus'}
        }
    ]

    def calculate(self, locus):
        return locus.qual

