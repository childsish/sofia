import string

from lhc.tool import enum
from collections import OrderedDict

Transform = enum(['NUC2NUC', 'NUC2PEP', 'NUC2STR', 'NUC2BPP'])

class Feature(object):
    def __init__(self):
        self.dependency = None
        self.transforms = OrderedDict()
        self.transforms[Transform.NUC2NUC] = string.lower
    
    def generate(self, obj):
        """ Generate the feature from the given object. This method should
            be used when you are not using the supporting structure to reduce
            redundant calculations.
        """
        dep_res = None
        if self.dependency is not None:
            self.dependency.instantiate()
            dep_res = self.dependency.instance.generate(obj)
        return self.calculate(obj, dep_res)
    
    def calculate(self, obj, dep_res=None):
        """ Calculate the feature from the dependencies. This method should
            be used when you are using the supporting structure that reduces
            redundant calculations.
        """
        raise NotImplementedError('You must override this function')
    
    def transform(self, obj):
        for v in self.transforms.itervalues():
            obj = v(obj)
        return obj


class Dependency(object):
    def __init__(self, class_, *args, **kwargs):
        self.class_ = class_
        self.args = args
        self.kwargs = kwargs
        self.instance = None
    
    def instantiate(self):
        if self.instance is None:
            self.instance = self.class_(*self.args, **self.kwargs)
        return self.instance
    
    def setInstance(self, instance):
        self.instance = instance
