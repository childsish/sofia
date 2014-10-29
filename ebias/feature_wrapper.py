from ebias.entity import Entity

class FeatureWrapper(object):
    def __init__(self, feature_class, name=None, ins=None, outs=None, param={}, attr={}):
        self.feature_class = feature_class
        self.name = feature_class.__name__ if name is None else name
        self.ins = {in_: Entity(in_) for in_ in feature_class.IN}\
            if ins is None else ins
        self.outs = {out: Entity(out) for out in feature_class.OUT}\
            if outs is None else outs
        self.param = param
        self.attr = attr

    def __str__(self):
        return self.name

    def __call__(self, resources=None, dependencies=None, ins=None, outs=None):
        ins = self.ins if ins is None else ins
        outs = self.outs if outs is None else outs
        return self.feature_class(resources, dependencies, self.param, ins, outs)

    def getOutput(self, ins, requested_attr={}):
        return self.feature_class.getOutput(ins, self.outs, requested_attr)
