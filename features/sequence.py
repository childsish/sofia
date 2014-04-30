from itertools import izip
from modules.feature import Feature
from resource import StaticResource, DynamicResource
from lhc.binf.genetic_code import GeneticCodes

class Sequence(Feature):
    
    NAME = 'seq'
    RESOURCES = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'mdl',
         'feature': DynamicResource,
         'resource_map': {'name': 'mdl'}
        },
        {'name': 'seq',
         'feature': StaticResource,
         'resource_map': {'name': 'seq'}
        }
    ]
    
    def calculate(self, mdl, seq):
        res = {}
        for m in mdl:
            for k, v in m.transcripts.iteritems():
                res[k] = v.getSubSeq(seq, valid_types=set(['CDS']))
        return res
    
    def format(self, entity):
        if len(entity) == 0:
            return ''
        return str(entity)

class ProteinSequence(Feature):
    
    NAME = 'protein'
    RESOURCES = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'seq',
         'feature': Sequence,
         'resource_map': {'mdl': 'mdl', 'seq': 'seq'}
        }
    ]
    
    def __init__(self, resource_map, resources=None):
        super(ProteinSequence, self).__init__(resource_map, resources)
        self.gc = GeneticCodes()[1]
    
    def calculate(self, seq):
        res = {}
        for hdr, seq in seq.iteritems():
            it = iter(seq)
            protein = (self.gc[codon] for codon in izip(it, it, it))
            res[hdr] = ''.join(protein)
        return res
        
    def format(self, entity):
        if len(entity) == 0:
            return ''
        return str(entity)
