from collections import OrderedDict

class Generator(object):
    def __init__(self, features):
        self.features = OrderedDict()
        for feature in features:
            self.registerFeature(feature)
    
    def registerFeature(self, feature):
        self.features[feature.__name__] = feature
        if feature.dependency is not None:
            key = feature.dependency.class_.__name__
            self.features[key] = feature.dependency.instantiate()
    
    def generate(self, seq):
        res = OrderedDict()
        for name, feature in self.features.iteritems():
            for k, v in feature.generate(seq):
                res[k] = v
        return res
    
class RandomGenerator(Generator):
    def generate(self, seq):
        res = OrderedDict()
        for name, feature in self.features.iteritems():
            for k, v in feature.generate(seq):
                res[k] = v
        return res
        
