from collections import OrderedDict
from lhc.tool import combinations_with_replacement
from lhc.file_format.fasta import iterFasta

class CodonUsageTable(object):
    def __init__(self):
        self.cut = OrderedDict((''.join(cdn), 0)\
            for cdn in combinations_with_replacement('acgt', 3))
    
    def __str__(self):
        return '\n'.join('%s\t%s'%e for e in self.cut.iteritems())

    def __getitem__(self, key):
        return self.cut[key]
    
    def __setitem__(self, key, value):
        self.cut[key] = value
    
    def __contains__(self, key):
        return key in self.cut
    
    def normaliseByTotal(self):
        ttl = float(sum(cnt for cnt in self.cut.itervalues()))
        res = CodonUsageTable()
        for cdn, cnt in self.cut.iteritems():
            res[cdn] = cnt / ttl
        return res
    
    def normaliseByClass(self, genetic_code):
        ttls = {aa: sum(self.cut[cdn] for cdn in genetic_code[aa])\
            for aa in genetic_code.AMINO_ACIDS}
        res = CodonUsageTable()
        for cdn, cnt in self.cut.iteritems():
            res[cdn] = cnt / ttls[genetic_code[cdn]]
        return res
    
def createCutFromFasta(fname):
    return createCutFromSeqs(seq for hdr, seq in iterFasta(fname))

def createCutFromSeqs(seqs):
    res = CodonUsageTable()
    for seq in seqs:
        for i in xrange(0, len(seq), 3):
            cdn = seq[i:i+3].lower().replace('u', 't')
            if cdn in res:
                res[cdn] += 1
    return res
