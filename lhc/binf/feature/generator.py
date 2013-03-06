from collections import OrderedDict

class Generator(object):
    def __init__(self):
        self.features = OrderedDict()
    
    def registerFeature(self, feature):
        self.features[feature.name] = feature
    
    def generate(self, seq):
        res = OrderedDict()
        for name, feature in self.features.iteritems():
            res[name] = feature.calculate(seq)
        return res
