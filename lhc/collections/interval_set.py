__author__ = 'Liam Childs'

from collections import defaultdict
from lhc.interval import IntervalBinner as Binner


class IntervalSet(object):
    def __init__(self, intervals=None):
        self.len = 0
        self.binner = Binner()
        self.bins = defaultdict(list)

        if intervals is not None:
            for interval in intervals:
                self.add(interval)

    def __len__(self):
        return self.len

    def __contains__(self, item):
        bins = self.binner.get_overlapping_bins(item)
        for fr, to in bins:
            for bin in xrange(fr, to + 1):
                for interval in self.bins[bin]:
                    if interval == item:
                        return True
        return False

    def add(self, item):
        self.len += 1
        self.bins[self.binner.get_bin(item)].append(item)

    def fetch(self, item):
        bins = self.binner.get_overlapping_bins(item)
        for fr, to in bins:
            for bin in xrange(fr, to + 1):
                for interval in self.bins[bin]:
                    if interval.overlaps(item):
                        yield interval
