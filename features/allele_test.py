from modules.feature import Feature
from allele_count import AlleleCount

class AlleleTest(Feature):
    
    RESOURCES = ['db1', 'db2']
    DEPENDENCIES = [
        {'name': 'alf1',
         'feature': AlleleCount,
         'kwargs': {'db': 'db1'}
        },
        {'name': 'alf2',
         'feature': AlleleCount,
         'kwargs': {'db': 'db2'}
        }
    ]
    
    def calculate(self, entities):
        return ttest(hstack([entities['alf1'], entities['alf2']]))
