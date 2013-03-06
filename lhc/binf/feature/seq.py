#!/usr/bin/python

import string

from lhc.tool import window, combinations_with_replacement as genKmers
from collections import Counter, OrderedDict
from feature import Feature

class NucleotideFrequency(Feature):
    def __init__(self, k):
        self.k = k
        self.transform = [string.lower]
    
    def calculate(self, seq):
        res = OrderedDict((''.join(kmer), 0) for kmer in\
            genKmers('tgca', self.k))
        res.update(Counter(''.join(kmer) for kmer in\
            window(seq, self.k)).iteritems())
        return res
    
class NucleotideSkew(Feature):
    def __init__(self):
        self.depends = [(NucleotideFrequency, 1)]
        self.transform = [string.lower]
    
    def calculate(self, frq):
        res = OrderedDict([
            ('at', (frq['a'] - frq['t']) / (frq['a'] + frq['t'])),
            ('gc', (frq['g'] - frq['c']) / (frq['g'] + frq['c']))
        ])
