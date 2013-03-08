import numpy as np

from itertools import izip
from lhc.tool import window, combinations_with_replacement as genKmers, gmean
from collections import Counter, OrderedDict
from feature import Feature, Dependency

class CodonUsage(Feature):
    def __init__(self):
        super(CodonUsage, self).__init__()

    def calculate(self, seq, dep_res):
        res = OrderedDict((''.join(kmer), 0) for kmer in\
            genKmers('tgca', 3))
        res.update(Counter(seq[i:i+3] for i in xrange(0, len(seq), 3)))
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
            if cdn not in ['atg', 'tgg']:
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
