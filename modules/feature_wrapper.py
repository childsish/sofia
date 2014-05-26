from modules.resource import Resource, Target

class FeatureWrapper(object):
    def __init__(self, feature, name=None, out=None):
        self.feature = feature
        self.name = feature.__name__ if name is None else name
        self.in_ = feature.IN
        self.out = feature.OUT if out is None else out
        self.entities = {}

    def instantiate(self, dependencies, requested_resources, resources):
        if len(self.out) == 0:
            raise RuntimeError('You must specify output types for %s'%self.name)
        feature_name = (self.name, requested_resources)
        if issubclass(self.feature, Target):
            name, out, fname = resources['target']
            feature = self.feature(feature_name, dependencies, fname)
        elif issubclass(self.feature, Resource):
            name, out, fname = resources[self.name]
            feature = self.feature(feature_name, dependencies, fname)
        else:
            feature = self.feature(feature_name, dependencies)
        feature.in_ = self.in_
        feature.out = self.out
        return feature
