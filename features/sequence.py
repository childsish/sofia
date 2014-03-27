from collections import Counter
from modules.feature import Feature
from resource import StaticResource, DynamicResource

class Sequence(Feature):
    
    NAME = 'seq'
    RESOURCES = ['seq', 'mdl']
    DEPENDENCIES = [
        {'name': 'seq',
         'feature': StaticResource,
         'resource_map': {'name': 'seq'}
        },
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        }
    ]
    
    def calculate(self, seq, mdl):
        return mdl.getSubSeq(seq)
