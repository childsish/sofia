import itertools
import functools

from bisect import bisect_left
from collections import MutableSet


@functools.total_ordering
class SortedSet(MutableSet):
    def __init__(self, iterable=None, key=None, reversed=False):
        self.key = (lambda x: x) if key is None else key
        self.reversed = reversed
        if iterable is None:
            self.keys = []
            self.values = []
        else:
            self.keys, self.values =\
                [list(r) for r in itertools.izip(*sorted((self.key(item), item) for item in iterable))]

    def __str__(self):
        return 'SortedSet(%s)'.format(self.values)

    def __iter__(self):
        return reversed(self.values) if self.reversed else iter(self.values)

    def __len__(self):
        return len(self.values)

    def __contains__(self, item):
        idx = bisect_left(self.values, item)
        return idx < len(self.values) and self.values[idx] == item

    def __eq__(self, other):
        return set(self.values) == set(other)

    def __lt__(self, other):
        return set(self.values) < set(other)

    def __or__(self, other):
        return SortedSet(set(self.values) | other)

    def __and__(self, other):
        return SortedSet(set(self.values) & other)

    def __sub__(self, other):
        return SortedSet(set(self.values) - other)

    def __iand__(self, it):
        return super(SortedSet, self).__iand__(it)

    def isdisjoint(self, other):
        return super(SortedSet, self).isdisjoint(other)

    def __ixor__(self, it):
        return super(SortedSet, self).__ixor__(it)

    def clear(self):
        self.keys.clear()
        self.values.clear()

    def __rsub__(self, other):
        return super(SortedSet, self).__rsub__(other)

    @classmethod
    def __subclasshook__(cls, C):
        return super(SortedSet, cls).__subclasshook__(C)

    def pop(self):
        self.keys.pop()
        return self.values.pop()

    def remove(self, value):
        key = self.key(value)
        idx = bisect_left(self.keys, key)
        if idx < len(self.keys) and self.keys[idx] == key:
            self.keys.pop(idx)
            self.values.pop(idx)

    def _hash(self):
        return hash(self.values)

    @classmethod
    def _from_iterable(cls, it):
        return super(SortedSet, cls)._from_iterable(it)

    def __ior__(self, it):
        return super(SortedSet, self).__ior__(it)

    def discard(self, value):
        pass

    def __xor__(self, other):
        return super(SortedSet, self).__xor__(other)

    def __isub__(self, it):
        return super(SortedSet, self).__isub__(it)

    def add(self, value):
        key = self.key(value)
        idx = bisect_left(self.keys, key)
        if idx >= len(self.values) or self.values[idx] != value:
            self.keys.insert(idx, key)
            self.values.insert(idx, value)

    def pop_lowest(self):
        return self.values.pop(0)

    def pop_highest(self):
        return self.values.pop()
