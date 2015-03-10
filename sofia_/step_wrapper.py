from sofia_.entity import Entity


class StepWrapper(object):
    def __init__(self, step_class, name=None, ins=None, outs=None, param={}, attr={}):
        self.action_class = step_class
        self.name = step_class.__name__ if name is None else name
        self.ins = {in_: Entity(in_) for in_ in step_class.IN}\
            if ins is None else ins
        self.outs = {out: Entity(out) for out in step_class.OUT}\
            if outs is None else outs
        self.param = param
        self.attr = attr

    def __str__(self):
        return self.name

    def __call__(self, resources=None, dependencies=None, ins=None, outs=None, converters={}):
        ins = self.ins if ins is None else ins
        outs = self.outs if outs is None else outs
        return self.action_class(resources, dependencies, self.param, ins, outs, converters, self.name)

    def get_output(self, ins, requested_attr={}, entity_graph=None):
        attr = self.attr.copy()
        attr.update(requested_attr)
        return self.action_class.get_output(ins, self.outs, attr, entity_graph)
