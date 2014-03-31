from modules.feature import Feature
from resource import DynamicResource

class Gene(Feature):
    
    NAME = 'gene_name'
    RESOURCES = ['mdl']
    DEPENDENCIES = [
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        }
    ]
    
    def calculate(self, mdl):
        return mdl.name
