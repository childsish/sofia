from modules.feature import Feature
from modules.resource import Resource
from sequence import Sequence

class Gene(Feature):
    
    NAME = 'gene'
    RESOURCES = ['mdl']
    DEPENDENCIES = [
        {'name': 'mdl',
         'feature': Resource,
         'resource_map': {'name': 'mdl'}
        }
    ]
    
    def calculate(self, target, mdl):
        return mdl.name
