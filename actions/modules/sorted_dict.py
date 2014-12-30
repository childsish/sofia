from bisect import bisect_left
from itertools import izip


class SortedDict(object):
    """ A dictionary sorted by key.
    """
    def __init__(self, iterable=[], key=None):
        """Create a sorted dictionary
        
        :param iterable: the initial key:value pairs to put in the dictionary
        :type iterable: list of tuple
        """
        self._keys = []
        self.keys = []
        self.values = []
        self.key = (lambda x: x) if key is None else key
        for item in iterable:
            self[item[0]] = item[1]

    def __str__(self):
        return '{{{}}}'.format(', '.join(['{}:{}'.format(entry) for entry in self.iteritems()]))

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        idx = bisect_left(self._keys, self.key(key))
        return idx < len(self.keys) and self.keys[idx] == key

    def __getitem__(self, key):
        idx = bisect_left(self._keys, self.key(key))
        if self.keys[idx] != key:
            raise KeyError(key)
        return self.values[idx]

    def __setitem__(self, key, value):
        _key = self.key(key)
        idx = bisect_left(self._keys, _key)
        if idx >= len(self.keys) or self.keys[idx] != key:
            self._keys.insert(idx, _key)
            self.keys.insert(idx, key)
            self.values.insert(idx, value)
        else:
            self.values[idx] = value

    def get(self, key, default):
        _key = self.key(key)
        idx = bisect_left(self._keys, _key)
        if idx >= len(self.keys) or self.keys[idx] != key:
            self._keys.insert(idx, _key)
            self.keys.insert(idx, key)
            self.values.insert(idx, default)
        return self.values[idx]

    def iterkeys(self):
        return iter(self.keys)

    def itervalues(self):
        return iter(self.values)

    def iteritems(self):
        return izip(self.keys, self.values)

    def pop_highest(self):
        self._keys.pop()
        return self.keys.pop(), self.values.pop()

    def pop_lowest(self):
        self._keys.pop(0)
        return self.keys.pop(0), self.values.pop(0)
