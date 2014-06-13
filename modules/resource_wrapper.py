import os

from modules.resource import Resource, Target

class ResourceWrapper(object):
    def __init__(self, parser, name=None, out=None):
        self.parser = parser
        self.name = os.path.split(parser.fname)[1] if name is None else name
        self.in_ = []
        self.out = [] if out is None else out

    def instantiate(self, name, dependencies, requested_resources, resources):
        resource = Resource(name, dependencies, self.parser)
        resource.out = self.out
        return resource
