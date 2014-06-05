from modules.resource import Resource, Target

class ResourceWrapper(object):
    def __init__(self, fname, out=None):
        self.in_ = []
        self.out = fname.rsplit('.', 1)[-1:] if out is None else out
        self.fname = fname
        self.name = '%sResource'%self.out[0].capitalize()

    def instantiate(self, name, dependencies, requested_resources, resources):
        resource = Resource(name, dependencies, self.fname)
        resource.in_ = self.in_
        resource.out = self.out
        return resource

class TargetWrapper(object):
    def __init__(self, fname, out=None):
        self.in_ = []
        self.out = fname.rsplit('.', 1)[-1:] if out is None else out
        self.fname = fname
        self.name = 'Target'

    def instantiate(self, name, dependencies, requested_resources, resources):
        target = Target(name, dependencies, self.fname)
        target.in_ = self.in_
        target.out = self.out
        return target
