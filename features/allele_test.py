from modules.feature import Feature
from allele import AlleleCount

class AlleleTest(Feature):
    
    NAME = 'allele_test'
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
