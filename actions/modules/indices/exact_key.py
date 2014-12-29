from index import Accessor


class ExactKeyIndex(Accessor):
    
    __slots__ = ('index',)
    
    RETURN = 'single'
    TYPE = 'exact'
    
    def __init__(self):
        self.index = {}
    
    def __contains__(self, key):
        return key in self.index
    
    def __getitem__(self, key):
        return self.index[key]
    
    def __setitem__(self, key, value):
        self.index[key] = value

    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate__(self, state):
        for attr in self.__slots__:
            setattr(self, attr, state[attr])

