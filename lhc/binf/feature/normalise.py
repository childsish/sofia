from feature import Feature, Dependency

class LengthNormalised(Feature):
    def __init__(self, dependency):
        super(NormaliseLength, self).__init__()
        self.dependency = dependency
    
    def calculate(self, obj, dep_res):
        for k in dep_res:
            dep_res[k] /= len(obj)
        return dep_res
