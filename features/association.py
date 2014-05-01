from modules.feature import Feature
from resource import DynamicResource

class AssociationPvalue(Feature):
    
    NAME = 'pvalue'
    RESOURCES = ['pseq']
    DEPENDENCIES = [
        {'name': 'pseq',
         'feature': DynamicResource,
         'resource_map': {'name': 'pseq'}
        }
    ]
    
    def calculate(self, pseq):
        if pseq is None:
            return 'NA'
        return pseq.p

    def format(self, entity):
        if isinstance(entity, basestring):
            return entity
        return '%.3f'%entity
 
