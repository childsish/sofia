from sofia_.entity import Entity

class ActionWrapper(object):
    def __init__(self, action_class, name=None, ins=None, outs=None, param={}, attr={}):
        self.action_class = action_class
        self.name = action_class.__name__ if name is None else name
        self.ins = {in_: Entity(in_) for in_ in action_class.IN}\
            if ins is None else ins
        self.outs = {out: Entity(out) for out in action_class.OUT}\
            if outs is None else outs
        self.param = param
        self.attr = attr

    def __str__(self):
        return self.name

    def __call__(self, resources=None, dependencies=None, ins=None, outs=None, converters={}):
        ins = self.ins if ins is None else ins
        outs = self.outs if outs is None else outs
        return self.action_class(resources, dependencies, self.param, ins, outs, converters)

    def getOutput(self, ins, requested_attr={}):
        return self.action_class.getOutput(ins, self.outs, requested_attr)
