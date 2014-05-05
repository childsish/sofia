import sys

from modules.feature import Feature
from resource import DynamicResource

class GeneName(Feature):
    
    NAME = 'gene_name'
    RESOURCES = ['mdl']
    DEPENDENCIES = [
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        }
    ]
    
    def calculate(self, mdl):
        if mdl is not None:
            return ','.join(m.name for m in mdl)
        return ''

