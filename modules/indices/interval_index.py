import cPickle
import os

from bisect import bisect
from operator import add
from index import Index

class IntervalIndex(Index):
    
    MINBIN = 2
    MAXBIN = 7
    
    def __init__(self, iname):
        self.iname = iname
        self.index = {}
        if os.path.exists(iname):
            infile = open(iname)
            self.index = cPickle.load(infile)
            infile.close()
    
    def __getitem__(self, key):
        res = []
        bins = self._getOverlappngBins(key)
        for bin in bins:
            if bin[0] == bin[1]:
                fr = to = bisect(self.bins, bin[0])
            else:
                fr = bisect(self.bins[0], bin[0])
                to = bisect(self.bins[1], bin[1])
            res.extend(self.values[idx] for idx in xrange(fr, to))
        return (fpos
            for fpos, ivl in
                (self.values[idx] for idx in reduce(add, res))
            if ivl.overlaps(key))
    
    def __setitem__(self, key, value):
        pass
    
    def __del__(self):
        outfile = open(self.iname, 'w')
        cPickle.dump(self.index, outfile)
        outfile.close()

    @classmethod
    def _getBin(cls, ivl):
        for i in range(cls.MINBIN, cls.MAXBIN + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.end / binLevel):
                return int(i * 10 ** (self.MAXBIN + 1) + int(ivl.start / binLevel))
        return int((cls.MAXBIN + 1) * 10 ** (cls.MAXBIN + 1))
    
    @classmethod
    def _getOverlappingBins(cls, ivl):
        res = []
        bigBin = int((cls.MAXBIN + 1) * 10 ** (cls.MAXBIN + 1))
        for i in range(cls.MINBIN, cls.MAXBIN + 1):
            binLevel = 10 ** i
            res.append((int(i * 10 ** (cls.MAXBIN + 1) + int(ivl.start / binLevel)), int(i * 10 ** (cls.MAXBIN + 1) + int(ivl.end / binLevel))))
            res.append((bigBin, bigBin))
        return res
