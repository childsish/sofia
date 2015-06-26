__author__ = 'Liam Childs'

import bisect

from operator import or_


class Track(object):
    def __init__(self, intervals=[]):
        self.starts = []
        self.stops = []
        self.blocks = []

        for interval in intervals:
            self[interval] = interval.data

    def __contains__(self, item):
        fr, to = self._intersect(item)
        return fr != to

    def __getitem__(self, item):
        fr, to = self._intersect(item)
        return reduce(or_, (self.blocks[i] for i in xrange(fr, to)), set())

    def __setitem__(self, key, value):
        fr, to = self._intersect(key)
        idxs = range(fr, to)
        if len(idxs) > 0:
            start = min(key.start, *[self.starts[i] for i in idxs])
            stop = max(key.stop, *[self.stops[i] for i in idxs])
            blocks = self[key] | {value}
            for i in reversed(idxs):
                del self.starts[i]
                del self.stops[i]
                del self.blocks[i]
        else:
            start = key.start
            stop = key.stop
            blocks = {value}
        self.starts.insert(fr, start)
        self.stops.insert(fr, stop)
        self.blocks.insert(fr, blocks)

    def get_cost(self, interval=None, block=None):
        lens = [len(b) for b in self.blocks]
        if interval is not None:
            if block is None:
                raise ValueError('block must be passed along with the interval')
            fr, to = self._intersect(interval)
            idxs = range(fr, to)
            if len(idxs) > 0:
                lens.append(len(self[interval] | {block}))
                for i in reversed(idxs):
                    del lens[i]
            else:
                lens.append(1)
        return sum(lens) / float(len(lens))

    def _intersect(self, interval):
        return bisect.bisect_right(self.stops, interval.start),\
            bisect.bisect_left(self.starts, interval.stop)
