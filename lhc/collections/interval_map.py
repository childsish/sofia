__author__ = 'Liam Childs'

from collections import defaultdict
from lhc.interval import IntervalBinner


class IntervalMap(object):
    def __init__(self, key_value_pairs=None):
        self.len = 0
        self.binner = IntervalBinner()
        self.bins = defaultdict(list)
        self.values = defaultdict(list)

        if key_value_pairs is not None:
            for key, value in key_value_pairs:
                self[key] = value

    def __len__(self):
        return self.len

    def __contains__(self, item):
        bins = self.binner.get_overlapping_bins(item)
        for fr, to in bins:
            for bin in xrange(fr, to + 1):
                for set_interval in self.bins[bin]:
                    if set_interval == item:
                        return True
        return False

    def __setitem__(self, key, value):
        self.len += 1
        bin = self.binner.get_bin(key)
        self.bins[bin].append(key)
        self.values[bin].append(value)

    def __getitem__(self, item):
        bins = self.binner.get_overlapping_bins(item)
        for fr, to in bins:
            for bin in xrange(fr, to + 1):
                for i, set_interval in enumerate(self.bins[bin]):
                    if set_interval.overlaps(item):
                        yield self.values[bin][i]
