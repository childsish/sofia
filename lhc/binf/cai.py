#!/usr/bin/python

import numpy

from GeneticCode import GeneticCodes
from FileFormats.CodonUsageTable import CodonUsageTable
from scipy.stats.mstats import gmean # Geometric mean

class CodonAdaptationIndex(object):
    def __init__(self, cut, gc):
        self.cut = CodonUsageTable(cut)
        self.gc = GeneticCodes()[gc]
        
        # Calculate relative synonymous codon usage
        self.rscu = {}
        for aa in self.gc.AMINO_ACIDS:
            codons = self.gc.getCodons(aa)
            ttl = numpy.mean([self.cut[codon] for codon in codons])
            for codon in codons:
                self.rscu[codon] = self.cut[codon] / ttl
        
    def calculateCAI(self, seq):
        rscu = self.rscu
        gc = self.gc

        # Calculate the codon adaptation index
        cai_obs = []
        cai_max = []
        for i in xrange(0, len(seq) - 3, 3):
            cdn = seq[i:i+3]
            aa = gc.getAminoAcid(cdn)
            rscus = [rscu[cdn] for cdn in gc.getCodons(aa)]
            cai_obs.append(rscu[cdn])
            cai_max.append(max(rscus))
        ncodon = len(seq) / 3.0 - 1
        cai_obs = gmean(cai_obs)
        cai_max = gmean(cai_max)
        cai = cai_obs / cai_max
        return cai

