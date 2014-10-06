class FeatureWrapper(object):
    def __init__(self, feature_class, name=None, ins=None, outs=None, kwargs={}):
        self.feature_class = feature_class
        self.name = feature_class.__name__ if name is None else name
        self.ins = feature_class.IN if ins is None else ins
        self.outs = feature_class.OUT if outs is None else outs
        self.kwargs = kwargs

    def __call__(self, resources=None, dependencies=None, kwargs={}):
        tmp_kwargs = self.kwargs.copy()
        tmp_kwargs.update(kwargs)
        return self.feature_class(resources, dependencies, tmp_kwargs)
