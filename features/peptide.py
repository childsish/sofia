from collections import Counter
from modules.feature import Feature
from sequence import ProteinSequence
from lhc.binf.pest import Pest as PestBase

class PeptideFrequency(Feature):
    
    NAME = 'aa_freq'
    RESOURCES = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'protein',
         'feature': ProteinSequence,
         'resource_map': {'mdl': 'mdl', 'seq': 'seq'}
        }
    ]

    def calculate(self, protein):
        res = {}
        for hdr, seq in protein:
            cnt = Counter(protein)
            res[hdr] = cnt
        return res

class PEST(Feature):
    
    NAME = 'pest'
    RESOURCES = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'protein',
         'type': ProteinSequence,
         'resource_map': {'mdl': 'mdl', 'seq': 'seq'}
        }
    ]
    
    def __init__(self, resource_map, resources=None):
        super(PEST, self).__init__(resource_map, resources)
        self.pest = PestBase()

    def calculate(self, protein):
        return {hdr: list(self.pest.iterPest(seq)) for hdr, seq in protein.iteritems()}
