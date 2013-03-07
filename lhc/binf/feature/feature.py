class Feature(object):
    def __init__(self):
        self.depends = {}
        self.transform = []
    
    def registerDependency(self, dependency):
        self.depends[dependency.class_.__name__] = dependency
    
    def generate(self, obj):
        """ Generate the feature from the given object. This method should
            be used when you are not using the supporting structure to reduce
            redundant calculations.
        """
        raise NotImplementedError('You must override this function')
    
    def calculate(self):
        """ Calculate the feature from the dependencies. This method should
            be used when you are using the supporting structure that reduces
            redundant calculations.
        """
        raise NotImplementedError('You must override this function')


class Dependency(object):
    def __init__(self, class_, *args, **kwargs):
        self.class_ = class_
        self.args = args
        self.kwargs = kwargs
        self.instance = None
        self.instatiated = False
    
    def instantiate(self):
        self.instance = self.class_(*self.args, **self.kwargs)
        self.instantiated = True
        return self.instance
    
    def setInstance(self, instance):
        self.instance = instance
        self.instantiated = True
