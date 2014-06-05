class FeatureWrapper(object):
    def __init__(self, feature, out=None):
        self.feature = feature
        self.in_ = feature.IN
        self.out = feature.OUT if out is None else out
        self.name = feature.__name__

    def instantiate(self, name, dependencies, requested_resources, resources):
        if len(self.out) == 0:
            raise RuntimeError('You must specify output types for %s'%type(self.feature).__name__)
        feature = self.feature(name, dependencies)
        feature.in_ = self.in_
        feature.out = self.out
        return feature
