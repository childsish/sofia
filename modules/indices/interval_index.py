import cPickle
import os

from bisect import bisect_left, bisect_right
from operator import add
from index import Index

class IntervalIndex(Index):
    
    MINBIN = 2
    MAXBIN = 7
    
    def __init__(self):
        self.bins = []
        self.values = []
    
    def __getitem__(self, key):
        res = []
        bins = self._getOverlappingBins(key)
        for bin in bins:
            fr = bisect_left(self.bins, bin[0])
            to = bisect_right(self.bins, bin[1])
            res.extend(self.values[idx] for idx in xrange(fr, to))
        return [value for c_key, value in reduce(add, res, []) if key.overlaps(c_key)]
    
    def __setitem__(self, key, value):
        bin = self._getBin(key)
        idx = bisect_left(self.bins, bin)
        if idx >= len(self.bins) or self.bins[idx] != bin:
            self.bins.insert(idx, bin)
            self.values.insert(idx, [])
        self.values[idx].append((key, value))

    @classmethod
    def _getBin(cls, ivl):
        for i in range(cls.MINBIN, cls.MAXBIN + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.stop / binLevel):
                return int(i * 10 ** (cls.MAXBIN + 1) + int(ivl.start / binLevel))
        return int((cls.MAXBIN + 1) * 10 ** (cls.MAXBIN + 1))
    
    @classmethod
    def _getOverlappingBins(cls, ivl):
        res = []
        bigBin = int((cls.MAXBIN + 1) * 10 ** (cls.MAXBIN + 1))
        for i in range(cls.MINBIN, cls.MAXBIN + 1):
            binLevel = 10 ** i
            res.append((int(i * 10 ** (cls.MAXBIN + 1) + int(ivl.start / binLevel)), int(i * 10 ** (cls.MAXBIN + 1) + int(ivl.stop / binLevel))))
        res.append((bigBin, bigBin))
        return res
