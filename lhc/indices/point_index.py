from bisect import bisect_left, bisect_right
from lhc.indices.index import Index


class PointIndex(Index):

    RETURN = 'single'
    TYPE = 'inexact'
    
    def __init__(self):
        self.keys = []
        self.values = []
    
    def __contains__(self, key):
        idx = bisect_right(self.keys, key) - 1
        return self.keys[idx] == key
    
    def __getitem__(self, key):
        idx = bisect_right(self.keys, key) - 1
        return None if idx == -1 else self.values[idx]
    
    def __setitem__(self, key, value):
        idx = bisect_left(self.keys, key)
        if idx == len(self.keys) or self.keys[idx] != key:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)
        else:
            self.values[idx] = value
