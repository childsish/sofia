from collections import Counter, OrderedDict
from feature import Feature, Transform
from lhc.binf.pest import Pest as PestBase

class PeptideFrequency(Feature):
    def __init__(self, genetic_code):
        super(PeptideFrequency, self).__init__()
        self.transforms[Transform.NUC2PEP] = genetic_code.translate
        self.genetic_code = genetic_code
        
    def calculate(self, seq, dep_res):
        res = OrderedDict((aa, 0) for aa in self.genetic_code.AMINO_ACIDS)
        res['X'] = 0
        res.update(Counter(seq))
        if '*' in res:
            del res['*']
        return res

class Pest(Feature):
    def __init__(self, genetic_code, win=12, thr=5):
        super(Pest, self).__init__()
        self.transforms[Transform.NUC2PEP] = genetic_code.translate
        self.genetic_code = genetic_code
        self.pest = PestBase()
    
    def calculate(self, seq, dep_res):
        if seq.endswith('*'):
            seq = seq[:-1]
        psts = list(self.pest.iterPest(seq))
        return OrderedDict(
            npst = len(psts),
            avgpst = 'NA' if len(psts) == 0 else\
                sum(pst[0] for pst in psts) / float(len(psts)),
            maxpst = 'NA' if len(psts) == 0 else\
                max(pst[0] for pst in psts)
        )
