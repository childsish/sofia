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
        if issubclass(self.feature, Target):
            return self.feature('target', resources['target'])\
                if resources['target'][2].endswith(self.feature.EXT)\
                else None
        elif issubclass(self.feature, Resource):
            for resource in requested_resources:
                name, out, fname = resources[resource]
                if resource != 'target' and fname.endswith(self.feature.EXT):
                    return self.feature(resource, fname)
            return None
        return self.feature(dependencies)
