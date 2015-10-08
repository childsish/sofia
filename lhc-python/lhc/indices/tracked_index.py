__author__ = 'Liam Childs'

from Bio import bgzf
from bisect import bisect_left, bisect_right
from itertools import izip
from math import log
from operator import add
from lhc.interval import Interval


class TrackedIndex(object):
    def __init__(self, n):
        self.n = n
        self.tracks = [Track(n)]

    def add(self, item, offset):
        cost_increases = [(track.get_cost_increase(item, offset), i) for i, track in enumerate(self.tracks)]
        min_increase, index = min(cost_increases)
        self.tracks[index].add(item, offset)
        if index == len(self.tracks) - 1:
            self.tracks.append(Track(self.n))

    def fetch(self, *args):
        return reduce(add, (track.fetch(*args) for track in self.tracks))


class Track(object):
    def __init__(self, n):
        self.starts = []
        self.stops = []
        self.offsets = []
        self.n = n

    def add(self, interval, offset):
        """
        The added interval must be overlapping or beyond the last stored interval ie. added in sorted order.

        :param interval: interval to add
        :param offset: full virtual offset to add
        :return:
        """
        start, stop = self.get_start_stop(interval)

        if len(self.starts) > 0 and start < self.stops[-1]:
            if start < self.starts[-1] or offset < self.offsets[-1][1]:
                raise ValueError('intervals and offsets must be added in-order')
            self.stops[-1] = max(self.stops[-1], stop)
            self.offsets[-1][1] = offset
        else:
            self.starts.append(start)
            self.stops.append(stop)
            self.offsets.append([offset, offset])

    def fetch(self, *args):
        start, stop = self.get_start_stop(args)
        fr, to = self.get_overlapping_bounds(start, stop)
        return [self.offsets[i] for i in xrange(fr, to)]

    def get_overlapping_bounds(self, start, stop):
        return bisect_right(self.stops, start), bisect_left(self.starts, stop)

    def get_start_stop(self, item):
        start = [item[i].start if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        stop = [item[i].stop if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        if len(item) == self.n + 1:
            stop[-1] = item[-1]
        return start, stop

    def get_cost_increase(self, interval, offset):
        offsets = self.offsets

        if len(offsets) == 0:
            return 2
        start, stop = self.get_start_stop(interval)
        if start < self.starts[-1] or offset < offsets[-1][1]:
            raise ValueError('intervals must be added in-order')
        lens = [get_offset_count(fr, to) for fr, to in offsets]
        cost = log(len(lens), 2) + max(lens)
        if start < self.stops[-1]:
            lens[-1] = get_offset_count(offsets[-1][0], max(offsets[-1][1], offset))
        else:
            lens.append(1)
        return log(len(lens), 2) + max(lens) - cost


def multivariate_overlap(a, b):
    return all(univariate_overlap(ai, bi) for ai, bi in izip(a, b))


def univariate_overlap(a, b):
    a_start, a_stop = (a.start, a.stop) if isinstance(a, Interval) else (a, a)
    b_start, b_stop = (b.start, b.stop) if isinstance(b, Interval) else (b, b)
    return a_start == b_start or a_start < b_stop and b_start < a_stop


def get_item(starts, stops):
    return [start if start == stop else Interval(start, stop) for start, stop in izip(starts, stops)]


def get_offset_count(fr, to):
    block_fr, in_block_fr = bgzf.split_virtual_offset(fr)
    block_to, in_block_to = bgzf.split_virtual_offset(to)
    return block_to - block_fr + 1


def merge_offset_ranges(ranges, new_offset=None):
    mins, maxs = zip(*ranges)
    if new_offset is not None:
        maxs.append(new_offset)
    return min(mins), max(maxs)
