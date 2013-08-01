from bisect import bisect_left, bisect_right
from lhc.file_format.vcf import iterVcf

class VariantSet(object):
    def __init__(self, fname):
        self.poss = defaultdict(list)
        self.snps = defaultdict(list)
        for snp in iterVcf(fname):
            self.poss[snp.chm].append(snp.pos)
            self.snps[snp.chm].append(snp)
        for k in self.poss:
            self.poss[k].sort()
            self.snps[k].sort(key=lambda x:x.pos)
    
    def getRange(self, rng):
        poss = self.poss[rng.chm]
        idx_fr = bisect_left(poss, rng.fr)
        idx_to = bisect_right(poss, rng.to) + 1
        return self.snps[rng.chm][idx_fr:idx_to]
