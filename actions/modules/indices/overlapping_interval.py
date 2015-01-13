from collections import defaultdict
from indices.index import Accessor
from interval import Interval, IntervalBinner


class OverlappingIntervalIndex(Accessor):
    
    RETURN = 'multiple'
    TYPE = 'inexact'
    
    def __init__(self):
        self.binner = IntervalBinner()
        self.bins = defaultdict(dict)
    
    def __contains__(self, key):
        bin = self.binner.get_bin(key.start, key.stop)
        return bin in self.bins and key in self.bins[bin]
    
    def __getitem__(self, key):
        res = []
        bins = self.binner.get_overlapping_bins(key.start, key.stop)
        for bin_fr, bin_to in bins:
            if bin_fr == bin_to:
                if bin_fr not in self.bins:
                    continue
                res.extend(v for k, v in self.bins[bin_fr].iteritems() if k.overlaps(key))
            else:
                for bin in xrange(bin_fr, bin_to):
                    if bin not in self.bins:
                        continue
                    res.extend(v for k, v in self.bins[bin_fr].iteritems() if k.overlaps(key))
        return res
    
    def __setitem__(self, key, value):
        bin = self.binner.get_bin(key.start, key.stop)
        self.bins[bin][Interval(key.start, key.stop)] = value
    
    def __getstate__(self):
        return {
            'bins': self.bins,
            'minbin': self.binner.minbin,
            'maxbin': self.binner.maxbin
        }

    def __setstate__(self, state):
        self.bins = state['bins']
        self.binner = IntervalBinner(state['minbin'], state['maxbin'])
