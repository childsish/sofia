#!/usr/bin/python

import string

from lhc.tool import window, combinations_with_replacement as genKmers
from collections import Counter, OrderedDict
from feature import Feature, Dependency

class NucleotideFrequency(Feature):
    def __init__(self, k):
        super(NucleotideFrequency, self).__init__()
        self.transform.append(string.lower)
        self.k = k
    
    def generate(self, seq):
        res = OrderedDict((''.join(kmer), 0) for kmer in\
            genKmers('tgca', self.k))
        res.update(Counter(''.join(kmer) for kmer in\
            window(seq, self.k)).iteritems())
        return res
    
    def calculate(self, seq):
        return self.generate(seq)
 
class NucleotideSkew(Feature):
    def __init__(self):
        super(NucleotideSkew, self).__init__()
        self.registerDependency(Dependency(NucleotideFrequency, 1))
        self.transform = [string.lower]

    def generate(self, seq):
        instance = self.depends['NucleotideFrequency'].instance
        if instance is None:
            instance = self.depends['NucleotideFrequency'].instantiate()
        
        frq = instance.generate(seq)
        return self.calculate(frq)

    def calculate(self, frq):
        at = 0 if frq['a'] + frq['t'] == 0 else\
             (frq['a'] - frq['t']) / float(frq['a'] + frq['t'])
        gc = 0 if frq['g'] + frq['c'] == 0 else\
             (frq['g'] - frq['c']) / float(frq['g'] + frq['c'])
        res = OrderedDict([('at', at), ('gc', gc)])
        return res
