from collections import Counter
from modules.feature import Feature
from modules.resource import Resource

class AlleleCount(Feature):
    
    RESOURCES = ['db']
    DEPENDENCIES = [
        {'name': 'db',
         'feature': Resource,
         'kwargs': {'name': 'db'}
        }
    ]
    
    def calculate(self, target, entities=None):
        return Counter(entities['db'].samples)
