import bisect
import itertools

from collections import MutableSequence


class SortedList(MutableSequence):
    def __init__(self, iterable=None, key=None, reversed=False):
        self.key = (lambda x: x) if key is None else key
        self.reversed = reversed
        if iterable is None:
            self.keys = []
            self.values = []
        else:
            self.keys, self.values =\
                [list(r) for r in itertools.izip(*sorted((self.key(value), value) for value in iterable))]

    def __str__(self):
        return 'SortedList({})'.format(self.values)

    def __iter__(self):
        return reversed(self.values) if self.reversed else iter(self.values)

    def __reversed__(self):
        return iter(self.values) if self.reversed else reversed(self.values)

    def __len__(self):
        return len(self.values)

    def __contains__(self, value):
        idx = bisect.bisect_left(self.values, value)
        return idx < len(self.values) and self.values[idx] == value

    def __getitem__(self, key):
        idx = len(self.values) - key if self.reversed else key
        return self.values[idx]

    def __setitem__(self, key, value):
        idx = len(self.values) - key if self.reversed else key
        self.values[idx] = value

    def __delitem__(self, key):
        idx = len(self.values) - key if self.reversed else key
        del self.values[idx]

    def __iadd__(self, values):
        self.update(values)

    def append(self, value):
        idx = bisect.bisect_right(self.values)
        if idx != len(self.values):
            raise ValueError('Value out of bounds.')
        self.values.append(value)

    def add(self, value):
        key = self.key(value)
        idx = bisect.bisect_left(self.keys, key)
        self.keys.insert(idx, key)
        self.values.insert(idx, value)

    def count(self, value):
        return self.values.count(value)

    def extend(self, values):
        values = sorted(values)
        if values[0] < self.values[-1]:
            raise ValueError('Given values overlap existing values.')
        self.values.extend(values)

    def index(self, value):
        return self.values.index(value)

    def insert(self, index, value):
        if self.values[index] > value:
            raise ValueError('Value out-of-order.')
        self.values.insert(index, value)

    def pop(self, index=-1):
        self.values.pop(index)

    def remove(self, value):
        self.values.remove(value)

    def reverse(self):
        self.values.reverse()

    def update(self, other):
        self.values.extend(other)
        self.values.sort()
