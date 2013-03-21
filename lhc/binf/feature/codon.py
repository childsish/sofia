import numpy as np
import warnings

from itertools import izip
from lhc.tool import window, combinations_with_replacement as genKmers, gmean
from collections import Counter, OrderedDict, defaultdict
from feature import Feature, Dependency
from lhc.binf.genetic_code import RedundantCode
from lhc.binf.cut import createCutFromSeqs

class CodonUsage(Feature):
    def __init__(self, ignore_redundant=True):
        super(CodonUsage, self).__init__()
        self.ignore_redundant = ignore_redundant

    def calculate(self, seq, dep_res):
        res = OrderedDict((''.join(kmer), 0) for kmer in\
            genKmers('tgca', 3))
        res.update(Counter(seq[i:i+3] for i in xrange(0, len(seq), 3)))
        if self.ignore_redundant:
            for k in res:
                if len(set(k) & RedundantCode.REDUNDANT_BASES) > 0:
                    del res[k]
        return res

class CodonAdaptationIndex(Feature):
    def __init__(self, genetic_code, cut):
        super(CodonAdaptationIndex, self).__init__()
        self.genetic_code = genetic_code
        self.cut = cut
        self.rscu, self.w = self.calculateStatistics(self.cut)

    def calculate(self, seq, dep_res):
        gc = self.genetic_code
        cut = self.cut
        w = self.w
        cai = []
        for i in xrange(0, len(seq), 3):
            cdn = seq[i:i+3]
            red = set(cdn) & RedundantCode.REDUNDANT_BASES
            if len(red) > 0:
                warnings.warn('Redundant bases "%s" encountered in codon. Codon "%s" has been ignored.'%(','.join(sorted(red)), cdn))
                continue
            if cdn not in ['atg', 'tgg', 'taa', 'tga', 'tag']:
                cai.append(w[cdn])
        cai = np.array(cai)
        return {'cai': gmean(cai)}

    def calculateStatistics(self, cut):
        """ Calculates and return the relative synonymous codon usage (rscu) and
            relative codon adaptiveness (w).
        """
        gc = self.genetic_code
        rscu = {}
        w = {}
        for aa in gc.AMINO_ACIDS:
            cdns = gc.getCodons(aa)
            usgs = [cut[cdn] for cdn in cdns]
            rscus = [usg / np.mean(usgs) for usg in usgs]
            ws = [usg / max(usgs) for usg in usgs]
            for cdn, rscu_, w_ in izip(cdns, usgs, ws):
                rscu[cdn] = rscu_
                w[cdn] = w_
        return rscu, w

class EffectiveNumberOfCodons(Feature):
    def __init__(self, genetic_code):
        super(EffectiveNumberOfCodons, self).__init__()
        self.genetic_code = genetic_code
    
    def calculate(self, seq, dep_res):
        cut = createCutFromSeqs([seq])
        Fs = {aa: self.calculateF(cut, self.genetic_code[aa])\
            for aa in self.genetic_code.AMINO_ACIDS}
        fams = defaultdict(list)
        for aa in self.genetic_code.AMINO_ACIDS:
            fams[len(self.genetic_code[aa])].append(Fs[aa])
        Nc = sum(len(fam_Fs) if sz == 1 else len(fam_Fs) / np.mean(fam_Fs)\
            for sz, fam_Fs in fams.iteritems())
        return {'Nc': Nc}
    
    def calculateF(self, cut, fam):
        n = float(sum(cut[cdn] for cdn in fam))
        res = n * sum((cut[cdn] / n) ** 2 for cdn in fam) / (n - 1)
        return res
