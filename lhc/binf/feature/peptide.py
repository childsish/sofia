from collections import Counter, OrderedDict
from feature import Feature, Transform

class PeptideFrequency(Feature):
    def __init__(self, genetic_code):
        super(PeptideFrequency, self).__init__()
        self.transforms[Transform.NUC2PEP] = genetic_code.translate
        self.genetic_code = genetic_code
        
    def calculate(self, seq, dep_res):
        res = OrderedDict((aa, 0) for aa in self.genetic_code.AMINO_ACIDS)
        res.update(Counter(seq))
        if '*' in res:
            del res['*']
        return res
