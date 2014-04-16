from bisect import bisect_left
from itertools import izip

class SortedDict(object):
    def __init__(self):
        self.keys = []
        self.values = []
    
    def __iter__(self):
        return self.iterkeys()
    
    def __len__(self):
        return len(self.keys)
    
    def __contains__(self, key):
        idx = bisect_left(self.keys, key)
        return self.keys[idx] == key
    
    def __getitem__(self, key):
        idx = bisect_left(self.keys, key)
        if self.keys[idx] != key:
            raise KeyError(key)
        return self.keys[idx]

    def __setitem__(self, key, value):
        idx = bisect_left(self.keys, key)
        if self.keys[idx] == key:
            self.values[idx] = value
        else:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)
    
    def iterkeys(self):
        return iter(self.keys)
    
    def itervalues(self):
        return iter(self.values)
    
    def iteritems(self):
        return izip(self.keys, self.values)

    def popHighest(self):
        key = self.keys.pop()
        value = self.values.pop()
        return (key, value)

    def popLowest(self):
        key = self.keys.pop(0)
        value = self.values.pop(0)
        return (key, value)
