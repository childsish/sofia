from modules.feature import Feature
from resource import StaticResource, DynamicResource

class MatchVcf(Feature):
    
    NAME = 'match_vcf'
    RESOURCES = ['vcf']
    DEPENDENCIES = [
        {'name': 'vcf',
         'feature': DynamicResource,
         'resource_map': {'name': 'vcf'}
        }
    ]
    
    def calculate(self, vcf):
        return vcf is not None
 
