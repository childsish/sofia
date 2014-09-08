from bisect import bisect_left, bisect_right
from lhc.indices.index import Accessor
from lhc.interval import Interval, IntervalBinner

class OverlappingIntervalIndex(Accessor):
    
    __slots__ = ('bins', 'items')
    
    RETURN = 'multiple'
    TYPE = 'inexact'
    
    def __init__(self):
        self.binner = IntervalBinner()
        self.bins = []
        self.items = []
    
    def __contains__(self, key):
        bin = self.binner.getBin(key)
        idx = bisect_left(self.bins, bin)
        if idx == len(self.bins) or self.bins[idx] != bin:
            return False
        return key in self.items[idx]
    
    def __getitem__(self, key):
        res = []
        bins = self.binner.getOverlappingBins(key)
        for bin in bins:
            if bin[0] == bin[1]:
                idx = bisect_left(self.bins, bin[0])
                if idx == len(self.bins):
                    continue
                res.extend(v for k, v in sorted(self.items[idx].iteritems()) if k.overlaps(key))
            else:
                idx_fr = bisect_right(self.bins, bin[0])
                idx_to = bisect_right(self.bins, bin[1])
                if idx_fr == len(self.bins) and idx_to == len(self.bins):
                    continue
                for idx in xrange(idx_fr, idx_to):
                    res.extend(v for k, v in sorted(self.items[idx].iteritems()) if k.overlaps(key))
        return res
    
    def __setitem__(self, key, value):
        bin = self.binner.getBin(key)
        idx = bisect_left(self.bins, bin)
        if idx == len(self.bins) or self.bins[idx] != bin:
            self.bins.insert(idx, bin)
            self.items.insert(idx, {})
        self.items[idx][Interval(key.start, key.stop)] = value
    
    def _getBin(self, key):
        for i in range(self.MINBIN, self.MAXBIN + 1):
            binLevel = 10 ** i
            if int(key.start / binLevel) == int(key.stop / binLevel):
                return int(i * 10 ** (self.MAXBIN + 1) + int(key.start / binLevel))
        return int((self.MAXBIN + 1) * 10 ** (self.MAXBIN + 1))
    
    def _getOverlappingBins(self, key):
        res = []
        for i in range(self.MINBIN, self.MAXBIN + 1):
            binLevel = 10 ** i
            fr = int(i * 10 ** (self.MAXBIN + 1) + int(key.start / binLevel))
            to = int(i * 10 ** (self.MAXBIN + 1) + int(key.stop / binLevel))
            res.append((fr, to))
        bigBin = int((self.MAXBIN + 1) * 10 ** (self.MAXBIN + 1))
        res.append((bigBin, bigBin))
        return res


    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate__(self, state):
        for attr in self.__slots__:
            setattr(self, attr, state[attr])


