from collections import defaultdict
from lhc.indices.index import Accessor
from lhc.interval import Interval, IntervalBinner

class OverlappingIntervalIndex(Accessor):
    
    __slots__ = ('bins',)
    
    RETURN = 'multiple'
    TYPE = 'inexact'
    
    def __init__(self):
        self.binner = IntervalBinner()
        self.bins = defaultdict(dict)
    
    def __contains__(self, key):
        bin = self.binner.getBin(key)
        return bin in self.bins and key in self.bins[bin]
    
    def __getitem__(self, key):
        res = []
        bins = self.binner.getOverlappingBins(key)
        for bin_fr, bin_to in bins:
            if bin_fr == bin_to:
                if bin_fr not in self.bins:
                    continue
                res.extend(v for k, v in self.bins[bin_fr].iteritems()\
                    if k.overlaps(key))
            else:
                for bin in xrange(bin_fr, bin_to):
                    if bin not in self.bins:
                        continue
                    res.extend(v for k, v in self.bins[bin_fr].iteritems()\
                        if k.overlaps(key))
        return res
    
    def __setitem__(self, key, value):
        bin = self.binner.getBin(key)
        self.bins[bin][Interval(key.start, key.stop)] = value
    
    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate__(self, state):
        self.binner = IntervalBinner()
        for attr in self.__slots__:
            setattr(self, attr, state[attr])

