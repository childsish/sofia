from RNA import fold, pf_fold
from feature import Feature, Transform

class MinimumFreeEnergy(Feature):
    def __init__(self):
        super(MinimumFreeEnergy, self).__init__(self)
    
    def calculate(self, seq, dep_res):
        return {'mfe': RNA.fold()[1]}

class EnsembleFreeEnergy(Feature):
    def __init__(self):
        super(EnsembleFreeEnergy, self).__init__(self)
    
    def calculate(self, seq, dep_res):
        return {'efe': RNA.pf_fold()[1]}
