from ebias.entity import Entity

class FeatureWrapper(object):
    def __init__(self, feature_class, name=None, ins=None, outs=None, kwargs={}):
        self.feature_class = feature_class
        self.name = feature_class.__name__ if name is None else name
        self.ins = {in_: Entity(in_) for in_ in feature_class.IN}\
            if ins is None else ins
        self.outs = {out: Entity(out) for out in feature_class.OUT}\
            if outs is None else outs
        self.kwargs = kwargs

    def __call__(self, resources=None, dependencies=None, kwargs={}, ins=None, outs=None):
        tmp_kwargs = self.kwargs.copy()
        tmp_kwargs.update(kwargs)
        ins = self.ins if ins is None else ins
        outs = self.outs if outs is None else outs
        return self.feature_class(resources, dependencies, tmp_kwargs, ins, outs)

    def iterOutput(self, ins):
        for outs in self.feature_class.iterOutput(ins, self.outs):
            yield outs
