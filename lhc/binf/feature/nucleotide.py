#!/usr/bin/python

import string

from lhc.tool import window, combinations_with_replacement as genKmers
from collections import Counter, OrderedDict
from feature import Feature, Dependency

class NucleotideFrequency(Feature):
    def __init__(self, k):
        super(NucleotideFrequency, self).__init__()
        self.k = k
    
    def calculate(self, seq, dep_res):
        res = OrderedDict((''.join(kmer), 0) for kmer in\
            genKmers('tgca', self.k))
        if self.k > len(seq):
            for k in res:
                res[k] = 'NA'
        else:
            res.update(Counter(kmer for kmer in\
                window(seq, self.k, lambda x: ''.join(x))))
        return res
 
class NucleotideSkew(Feature):
    def __init__(self):
        super(NucleotideSkew, self).__init__()
        self.dependency = Dependency(NucleotideFrequency, 1)

    def calculate(self, seq, frq):
        if 'NA' in (frq['a'], frq['t']):
            at = 'NA'
        else:
            at = 0 if frq['a'] + frq['t'] == 0 else\
                 (frq['a'] - frq['t']) / float(frq['a'] + frq['t'])
        if 'NA' in (frq['g'], frq['g']):
            gc = 'NA'
        else:
            gc = 0 if frq['g'] + frq['c'] == 0 else\
                 (frq['g'] - frq['c']) / float(frq['g'] + frq['c'])
        res = OrderedDict([('at', at), ('gc', gc)])
        return res
