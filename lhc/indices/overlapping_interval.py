from collections import defaultdict
from lhc.indices.index import Accessor
from lhc.interval import IntervalBinner


class OverlappingIntervalIndex(Accessor):
    
    __slots__ = ('bins',)
    
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
            for bin in xrange(bin_fr, bin_to + (bin_fr == bin_to)):
                res.extend(v for k, v in self.bins.get(bin, []) if k.overlaps(key))
        return res
    
    def __setitem__(self, key, value):
        bin = self.binner.get_bin(key)
        self.bins[bin].append((key, value))
    
    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate__(self, state):
        self.binner = IntervalBinner()
        for attr in self.__slots__:
            setattr(self, attr, state[attr])
