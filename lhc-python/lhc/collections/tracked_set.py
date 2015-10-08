__author__ = 'Liam Childs'

from bisect import bisect_left, bisect_right
from itertools import izip
from math import log
from operator import add
from lhc.interval import Interval


class TrackedSet(object):
    def __init__(self, n):
        self.n = n
        self.tracks = [Track(n)]

    def add(self, item):
        cost_increases = [(track.get_cost_increase(item), i) for i, track in enumerate(self.tracks)]
        min_increase, index = min(cost_increases)
        self.tracks[index].add(item)
        if index == len(self.tracks) - 1:
            self.tracks.append(Track(self.n))

    def fetch(self, *args):
        return reduce(add, (track.fetch(*args) for track in self.tracks))


class Track(object):
    def __init__(self, n):
        self.starts = []
        self.stops = []
        self.items = []
        self.n = n

    def add(self, item):
        start, stop = self.get_start_stop(item)
        fr, to = self.get_overlapping_bounds(start, stop)
        if fr == to:
            self.starts.insert(fr, start)
            self.stops.insert(fr, stop)
            self.items.insert(fr, [item])
        elif fr + 1 == to:
            self.starts[fr] = min(self.starts[fr], start)
            self.stops[fr] = max(self.stops[fr], stop)
            self.items[fr].append(item)
        else:
            self.starts[fr:to] = [min(self.starts[fr], start)]
            self.stops[fr:to] = [max(self.stops[to - 1], stop)]
            self.items[fr:to] = [reduce(add, self.items[fr:to])]
            self.items[fr].append(item)

    def fetch(self, *args):
        start, stop = self.get_start_stop(args)
        fr, to = self.get_overlapping_bounds(start, stop)
        query = get_item(start, stop) if len(args) == self.n + 1 else args
        res = []
        for index in xrange(fr, to):
            for item in self.items[index]:
                if multivariate_overlap(query, item):
                    res.append(item)
        return res

    def get_overlapping_bounds(self, start, stop):
        return bisect_right(self.stops, start), bisect_left(self.starts, stop)

    def get_start_stop(self, item):
        start = [item[i].start if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        stop = [item[i].stop if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        if len(item) == self.n + 1:
            stop[-1] = item[-1]
        return start, stop

    def get_cost_increase(self, item):
        if len(self.items) == 0:
            return 2
        lens = [len(items) for items in self.items]
        cost = log(len(lens), 2) + max(lens)
        start, stop = self.get_start_stop(item)
        fr, to = self.get_overlapping_bounds(start, stop)
        lens[fr:to] = [sum(lens[fr:to]) + 1]
        return log(len(lens), 2) + max(lens) - cost


def multivariate_overlap(a, b):
    return all(univariate_overlap(ai, bi) for ai, bi in izip(a, b))


def univariate_overlap(a, b):
    a_start, a_stop = (a.start, a.stop) if isinstance(a, Interval) else (a, a)
    b_start, b_stop = (b.start, b.stop) if isinstance(b, Interval) else (b, b)
    return a_start == b_start or a_start < b_stop and b_start < a_stop


def get_item(starts, stops):
    return [start if start == stop else Interval(start, stop) for start, stop in izip(starts, stops)]
