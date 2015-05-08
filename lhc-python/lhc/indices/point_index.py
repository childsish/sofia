from bisect import bisect
from lhc.indices.index import Index


class PointIndex(Index):

    RETURN = 'single'
    TYPE = 'inexact'
    
    def __init__(self):
        self.keys = []
        self.values = []
    
    def __contains__(self, key):
        return self.keys[bisect(self.keys, key) - 1] == key
    
    def __getitem__(self, key):
        idx = bisect(self.keys, key) - 1
        if idx < 0:
            raise KeyError(key)
        return self.values[idx]
    
    def __setitem__(self, key, value):
        idx = bisect(self.keys, key)
        if idx == len(self.keys) or self.keys[idx - 1] != key:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)
        else:
            self.values[idx] = value
