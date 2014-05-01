from collections import Counter
from modules.feature import Feature
from sequence import Sequence

class NucleotideFrequency(Feature):
    
    NAME = 'nt_freq'
    RESOURCE = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'seq',
         'feature': Sequence,
         'resource_map': {'mdl': 'mdl', 'seq': 'seq'}
        }
    ]
    
    def calculate(self, seq):
        res = {}
        for hdr, seq in seq.iteritems():
            cnt = Counter()
            for i in xrange(len(seq) - self.k + 1):
                cnt[seq[i:i + self.k]] += 1
            res[hdr] = cnt
        return res

class NucleotideSkew(Feature):
    
    NAME = 'nt_skew'
    RESOURCE = ['mdl', 'seq']
    DEPENDENCIES = [
        {'name': 'nt_freq',
         'feature': NucleotideFrequency,
         'resource_map': {'mdl': 'mdl', 'seq': 'seq'}
        }
    ]
    
    def calculate(self, nt_freq):
        res = {}
        for hdr, frq in nt_freq.iteritems():
            res[hdr] = {'at': (frq['a'] - frq['t']) / float(frq['a'] + frq['t']),
                        'gc': (frq['g'] - frq['c']) / float(frq['g'] + frq['c'])}
        return res
    
