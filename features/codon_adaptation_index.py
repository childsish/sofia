from modules.feature import Feature
from resource import StaticResource
from codon_usage_table import CodonUsageTable

class CodonAdaptationIndex(Feature):
    
    NAME = 'cai'
    RESOURCES = ['cut', 'seq', 'mdl']
    DEPENDENCIES = [
        {'name': 'cut1',
         'feature': StaticResource,
         'resource_map': {'name': 'cut'}
        },
        {'name': 'cut2',
         'feature': CodonUsageTable,
         'resource_map': {'seq': 'seq', 'mdl': 'mdl'}
        }
    ]
    
    def calculate(self, target, cut1, cut2):
        return cai(cut1, cut2)
