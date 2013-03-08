from feature import Feature, Transform
from lhc.binf.orf import findORFs

class ORFNumber(Feature):
    def __init__(self):
        super(ORFNumber, self).__init__()

    def calculate(self, seq, dep_res):
        return {'norf': len(findORFs(seq))}
