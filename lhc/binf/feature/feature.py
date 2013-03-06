class Feature(object):
    def __init__(self):
        self.depends = []
        self.supports = []
    
    def calculate(self, obj):
        raise NotImplementedError('You must override this function')
