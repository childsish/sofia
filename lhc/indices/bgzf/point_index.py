__author__ = 'Liam Childs'

from bisect import bisect_left, bisect_right
from operator import or_


class PointIndex(object):
    """
    Point index specifically used to index bgzf files. All values stored are the block offsets.
    """
    def __init__(self, index_classes=[]):
        self.keys = []
        self.values = []
        self.index_classes = index_classes
        self.is_leaf = len(index_classes) == 0

    def __contains__(self, item):
        if not self.is_leaf or len(item) == 1:
            fr, to = self._get_interval(item[0])
        elif len(item) == 2:
            fr, to = self._get_interval(item[0], item[1])
        else:
            raise KeyError('invalid key {}'.format(item))

        if self.is_leaf:
            return fr != to
        return fr != to and any(item[1:] in self.values[idx] for idx in xrange(fr, to))

    def __or__(self, other):
        if self.index_classes != other.index_classes:
            raise TypeError('incompatible index merge {} vs. {}'.format(self.index_classes, other.index_classes))
        res = PointIndex(self.index_classes)
        res.keys = self.keys[:]
        res.values = self.values[:]
        for key, value in zip(other.keys, other.values):
            idx = bisect_left(self.keys, key)
            if res.keys[idx] == key:
                res.values[idx] = res.values[idx] | other.values[idx]
            else:
                res.keys.insert(idx, key)
                res.values.insert(idx, value)
        return res

    def add(self, key, value):
        idx = bisect_left(self.keys, key[0])
        if idx >= len(self.keys) or self.keys[idx] != key[0]:
            self.keys.insert(idx, key[0])
            self.values.insert(idx, {value} if self.is_leaf else self._make_child())
        if not self.is_leaf:
            self.values[idx].add(key[1:], value)

    def fetch(self, *args):
        if not self.is_leaf or len(args) == 1:
            fr, to = self._get_interval(args[0])
            if fr >= len(self.keys) or self.keys[fr] != args[0]:
                raise KeyError(args[0])
        elif len(args) == 2:
            fr, to = self._get_interval(args[0], args[1])
        else:
            raise KeyError('invalid key {}'.format(args))

        if self.is_leaf:
            return reduce(or_, (self.values[idx] for idx in xrange(fr, to)), set())
        return reduce(or_, (self.values[idx].fetch(*args[1:]) for idx in xrange(fr, to)), set())

    def get_cost(self, key=None, value=None):
        """
        Worst case cost for accessing node.

        :param key: if specified, cost including this key and value
        :param value: if specified, cost including this key and value
        :return: cost for node access
        """
        if len(self.index_classes) == 0:
            return max(len(v) for v in self.values)
        return max(v.get_cost(None if key is None else key, value) for v in self.values)

    def _get_interval(self, start, stop=None):
        fr = bisect_left(self.keys, start)
        to = (fr + (fr < len(self.keys) and self.keys[fr] == start))\
            if stop is None else bisect_right(self.keys, stop)
        return fr, to

    def _make_child(self):
        return self.index_classes[0](self.index_classes[1:])

    # pickle helpers

    def __getstate__(self):
        values = self.values if self.is_leaf else [value.__getstate__() for value in self.values]
        return {
            'index_classes': self.index_classes,
            'keys': self.keys,
            'values': values
        }

    def __setstate__(self, state):
        self.index_classes = state['index_classes']
        self.keys = state['keys']
        self.values = state['values'] if self.is_leaf else\
            [self.init_from_state(state, self.index_classes) for state in state['values']]

    @staticmethod
    def init_from_state(state, index_classes):
        index = index_classes[0](index_classes[1:])
        index.__setstate__(state)
        return index
