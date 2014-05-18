from modules.resource import Resource, Target

class FeatureWrapper(object):
    def __init__(self, feature, name=None, out=None):
        self.feature = feature
        self.name = feature.__name__ if name is None else name
        self.in_ = feature.IN
        self.out = feature.OUT if out is None else out
        self.entities = {}

    def instantiate(self, requested_resources, resources):
        if len(self.out) == 0:
            raise RuntimeError('You must specify output types for %s'%self.name)
        if issubclass(self.feature, Target):
            return self.feature('target', resources['target'])\
                if resources['target'].endswith(self.feature.EXT)\
                else None
        elif issubclass(self.feature, Resource):
            for resource in requested_resources:
                if resource != 'target' and resources[resource].endswith(self.feature.EXT):
                    return self.feature(resource, resources[resource])
            return None
        return self.feature()
