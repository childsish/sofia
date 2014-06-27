class FeatureWrapper(object):
    def __init__(self, feature, name=None, out=None):
        self.feature = feature
        self.in_ = feature.IN
        self.out = feature.OUT if out is None else out
        self.name = feature.__name__ if name is None else name

    def instantiate(self, name, dependencies, requested_resources, resources):
        if len(self.out) == 0:
            raise RuntimeError('You must specify output types for %s'%type(self.feature).__name__)
        feature = self.feature(name, dependencies)
        feature.init()
        feature.in_ = self.in_
        feature.out = self.out
        return feature
