from bisect import bisect_left, bisect_right
from collections import defaultdict
from itertools import izip
from lhc.interval import interval

class IntervalSet(object):
    def __init__(self, ivls):
        ivls = sorted(ivls)
        self.frs = [ivl.start for ivl in ivls]
        self.tos = [ivl.stop for ivl in ivls]

    def __len__(self):
        return len(self.frs)
    
    def __getitem__(self, key):
        return interval(self.frs[key], self.tos[key])
    
    def __iter__(self):
        for fr, to in izip(self.frs, self.tos):
            yield interval(fr, to)
    
    def getOverlap(self, other):
        res = defaultdict(list)
        for sivl in self:
            fr_idx = bisect_right(other.tos, sivl.start)
            to_idx = bisect_left(other.frs, sivl.stop)
            for idx in xrange(fr_idx, to_idx):
                oivl = other[idx]
                if sivl and oivl:
                    res[sivl].append(oivl)
        return res
