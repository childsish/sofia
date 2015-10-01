__author__ = 'Liam Childs'

import bisect

from Bio.bgzf import split_virtual_offset
from operator import or_
from lhc.misc.tools import argsort
from itertools import izip


class Track(object):
    def __init__(self, index_classes=[]):
        self.starts = []
        self.stops = []
        self.values = []
        self.blocks = []
        self.index_classes = index_classes
        self.is_leaf = len(index_classes) == 0

    def __contains__(self, item):
        if not self.is_leaf or len(item) == 1:
            start, stop = (item[0].start, item[0].stop)\
                if hasattr(item[0], 'start') and hasattr(item[0], 'stop')\
                else (item[0], item[0] + 1)
            fr, to = self._get_interval(start, stop)
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
        res = Track(self.index_classes)
        starts = self.starts + other.starts
        stops = self.stops + other.stops
        values = self.values + other.values
        idxs = argsort(starts)
        c_start, c_stop, c_value = starts[idxs[0]], stops[idxs[0]], values[idxs[0]]
        for i, idx in enumerate(idxs):
            start, stop, value = starts[idx], stops[idx], values[idx]
            if start > c_stop:
                res.starts.append(c_start)
                res.stops.append(c_stop)
                res.values.append(c_value)
                c_start, c_stop = start, stop
            else:
                c_stop = max(c_stop, stop)
                c_value = c_value | value
        return res

    def add(self, key, value):
        block = split_virtual_offset(value)[0]
        fr, to = self._get_interval(key[0].start, key[0].stop)
        idxs = range(fr, to)
        if len(idxs) > 0:
            start = min(key[0].start, *[self.starts[i] for i in idxs])
            stop = max(key[0].stop, *[self.stops[i] for i in idxs])
            value = reduce(or_, (self.values[i] for i in idxs), {value})
            block = reduce(or_, (self.blocks[i] for i in idxs), {block})
            for i in reversed(idxs):
                del self.starts[i]
                del self.stops[i]
                del self.values[i]
                del self.blocks[i]
        else:
            start = key[0].start
            stop = key[0].stop
            block = {block}
            if self.is_leaf:
                value = {value}
            else:
                value = self._make_child()
                value.add(key[1:], value)
        self.starts.insert(fr, start)
        self.stops.insert(fr, stop)
        self.values.insert(fr, value)
        self.blocks.insert(fr, block)

    def fetch(self, *args):
        if not self.is_leaf or len(args) == 1:
            start, stop = (args[0].start, args[0].stop)\
                if hasattr(args[0], 'start') and hasattr(args[0], 'stop')\
                else (args[0], args[0] + 1)
        elif len(args) == 2:
            start, stop = args
        else:
            raise KeyError('invalid key {}'.format(args))

        fr, to = self._get_interval(start, stop)
        if self.is_leaf:
            return reduce(or_, (self.values[idx] for idx in xrange(fr, to)), set())
        return reduce(or_, (self.values[idx].fetch(*args[1:]) for idx in xrange(fr, to)), set())

    def fetch_blocks(self, *args):
        if not self.is_leaf or len(args) == 1:
            start, stop = (args[0].start, args[0].stop)\
                if hasattr(args[0], 'start') and hasattr(args[0], 'stop')\
                else (args[0], args[0] + 1)
        elif len(args) == 2:
            start, stop = args
        else:
            raise KeyError('invalid key {}'.format(args))

        fr, to = self._get_interval(start, stop)
        return reduce(or_, (self.blocks[idx] for idx in xrange(fr, to)), set())

    def get_cost(self, key=None, value=None):
        """
        Cost is the maximum number of blocks that would need to be accessed

        :param key: if specified, include the key in calculating costs
        :param value: if specified, include the value in calculating costs
        :return: cost for track access
        """
        costs = [len(blocks) for blocks in self.blocks]\
            if self.is_leaf\
            else [v.get_cost(None if key is None else key[1:], value) for v in self.values]
        if key is not None:
            if value is None:
                raise ValueError('block must be passed along with the interval')
            block = split_virtual_offset(value)[0]
            fr, to = self._get_interval(key[0].start, key[0].stop)
            idxs = range(fr, to)
            if len(idxs) > 0:
                costs.append(len(self.fetch_blocks(*key) | {block}))
                for i in reversed(idxs):
                    del costs[i]
            else:
                costs.append(1)
        return max(costs)

    def compress(self, factor=1):
        if not self.is_leaf:
            for i, value in enumerate(self.values):
                self.values[i] = value.compress(factor)
            return self

        it = izip(self.starts, self.stops, self.values)
        start, stop, value = it.next()
        res = Track(self.index_classes)
        res.starts.append(start)
        res.stops.append(stop)
        res.values.append(value.copy())

        c_factor = 1
        for start, stop, value in it:
            if value == res.values[-1] or c_factor < factor:
                res.stops[-1] = stop
                res.values[-1].update(value)
                c_factor += 1
            else:
                res.starts.append(start)
                res.stops.append(stop)
                res.values.append(value.copy())
                c_factor = 1
        return res

    def _get_interval(self, start, stop):
        return bisect.bisect_right(self.stops, start),\
            bisect.bisect_left(self.starts, stop)

    def _make_child(self):
        return self.index_classes[0](self.index_classes[1:])

    # pickle helpers

    def __getstate__(self):
        values = [list(v) for v in self.values] if self.is_leaf else [value.__getstate__() for value in self.values]
        return {
            'index_classes': self.index_classes,
            'starts': self.starts,
            'stops': self.stops,
            'values': values,
            'blocks': self.blocks
        }

    def __setstate__(self, state):
        self.index_classes = state['index_classes']
        self.starts = state['starts']
        self.stops = state['stops']
        self.values = set(state['values']) if self.is_leaf else\
            [self.init_from_state(state, self.index_classes) for state in state['values']]
        self.blocks = state['blocks']

    @staticmethod
    def init_from_state(state, index_classes):
        index = index_classes[0](index_classes[1:])
        index.__setstate__(state)
        return index
