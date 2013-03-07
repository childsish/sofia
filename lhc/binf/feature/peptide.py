import numpy as np

from collections import Counter, OrderedDict
from feature import Feature, Transform
from scipy.stats.mstats import gmean

class PeptideFrequency(Feature):
    def __init__(self, genetic_code):
        super(PeptideFrequency, self).__init__()
        self.transforms[Transform.NUC2PEP] = genetic_code.translate
        self.genetic_code = genetic_code
        
    def calculate(self, seq, dep_res):
        res = OrderedDict((aa, 0) for aa in self.genetic_code.AMINO_ACIDS)
        res.update(Counter(seq))
        return res

class CodonAdaptationIndex(Feature):
    def __init__(self, genetic_code, cut):
        super(CodonAdaptationIndex, self).__init__()
        self.transforms[Transform.NUC2PEP] = genetic_code.translate
        self.genetic_code = genetic_code
        self.cut = cut
        self.rscu = self.calculateRelativeSynonymousCodonUsage(cut)
    
    def calculate(self, seq, dep_res):
        gc = self.genetic_code
        rscu = self.rscu
        cai_obs = []
        cai_max = []
        for i in xrange(0, len(seq) - 3, 3):
            cdn = seq[i:i+3]
            aa = gc.getAminoAcid(cdn)
            rscus = [rscu[cdn] for cdn in gc.getCodons(aa)]
            cai_obs.append(rscu[cdn])
            cai_max.append(max(rscus))
        cai_obs = gmean(cai_obs)
        cai_max = gmean(cai_max)
        cai = cai_obs / cai_max
        return cai
    
    def calculateRelativeSynonymousCodonUsage(self, cut):
        gc = self.genetic_code
        print cut
        rscu = {}
        for aa in gc.AMINO_ACIDS:
            codons = gc.getCodons(aa)
            ttl = np.mean([self.cut[codon] for codon in codons])
            for codon in codons:
                self.rscu[codon] = self.cut[codon] / ttl
        print rscu
        return rscu
