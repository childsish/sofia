from collections import defaultdict
from lhc.indices.index import Index
from lhc.interval import IntervalBinner


class IntervalIndex(Index):
    
    RETURN = 'multiple'
    TYPE = 'inexact'
    
    def __init__(self):
        self.binner = IntervalBinner()
        self.bins = defaultdict(list)
    
    def __contains__(self, key):
        bin = self.binner.get_bin(key)
        return any(key == k for k, v in self.bins.get(bin, []))
    
    def __getitem__(self, key):
        res = []
        bins = self.binner.get_overlapping_bins(key)
        for bin_fr, bin_to in bins:
            for bin in xrange(bin_fr, bin_to + 1):
                res.extend(v for k, v in self.bins.get(bin, []) if k.overlaps(key))
        return res
    
    def __setitem__(self, key, value):
        bin = self.binner.get_bin(key)
        self.bins[bin].append((key, value))
