from bisect import bisect_left
from itertools import izip


class SortedDict(object):
    def __init__(self, iterable=None):
        """Create a sorted dictionary
        
        :param iterable: the initial key:value pairs to put in the dictionary
        :type iterable: list of tuple
        """
        if iterable is None:
            self.keys = []
            self.values = []
        else:
            self.keys, self.values = [list(r) for r in izip(*sorted(iterable))]
    
    def __str__(self):
        return '{%s}' % ', '.join(['%s:%s' % entry for entry in self.iteritems()])
    
    def __iter__(self):
        return self.iterkeys()
    
    def __len__(self):
        return len(self.keys)
    
    def __contains__(self, key):
        idx = bisect_left(self.keys, key)
        return idx < len(self.keys) and self.keys[idx] == key
    
    def __getitem__(self, key):
        idx = bisect_left(self.keys, key)
        if idx == len(self.keys) or self.keys[idx] != key:
            raise KeyError(key)
        return self.values[idx]

    def __setitem__(self, key, value):
        idx = bisect_left(self.keys, key)
        if idx >= len(self.keys) or self.keys[idx] != key:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)
        else:
            self.values[idx] = value

    def __delitem__(self, key):
        idx = bisect_left(self.keys, key)
        del self.keys[idx]
        del self.values[idx]
    
    def get(self, key, default):
        try:
            return self[key]
        except KeyError:
            pass
        return default
    
    def iterkeys(self):
        return iter(self.keys)
    
    def itervalues(self):
        return iter(self.values)
    
    def iteritems(self):
        return izip(self.keys, self.values)

    def pop_highest(self):
        key = self.keys.pop()
        value = self.values.pop()
        return key, value

    def pop_lowest(self):
        key = self.keys.pop(0)
        value = self.values.pop(0)
        return key, value
