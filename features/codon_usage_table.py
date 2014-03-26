from collections import Counter
from itertools import islice
from modules.feature import Feature
from sequence import Sequence

class CodonUsageTable(Feature):
    
    NAME = 'cut'
    RESOURCES = ['seq', 'mdl']
    DEPENDENCIES = [
        {'name': 'seq',
         'feature': Sequence,
         'resource_map': {'seq': 'seq', 'mdl': 'mdl'}
        }
    ]
    
    def calculate(self, target, seq):
        return Counter(islice(seq, 0, len(seq), 3))
