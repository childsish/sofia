__author__ = 'Liam Childs'

from collections import defaultdict
from lhc.interval import IntervalBinner as Binner


class IntervalBinner(object):
    def __init__(self, intervals):
        self.binner = Binner()
        self.bins = defaultdict(list)
        for interval in intervals:
            self.bins[self.binner.get_bin(interval)].append(interval)

    def intersect(self, interval):
        res = []
        bins = self.binner.get_overlapping_bins(interval)
        for fr, to in bins:
            for bin in xrange(fr, to):
                res.extend(set_interval for set_interval in self.bins[bin] if set_interval.overlaps(interval))
        return res
