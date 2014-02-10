import operator

from lhc import slicetools

class AugmentedTree(object):
    __slots__ = ('ivls', 'stops')
    
    def __init__(self, ivls):
        self.ivls = sorted(ivls, key=operator.attrgetter('start'))
        self.stops = [0 for ivl in ivls]
        self._refresh()
    
    def __iter__(self):
        return iter(self.ivls)
    
    def __getstate__(self):
        return {'ivls': self.ivls,
            'stops': self.stops}
    
    def __setstate__(self, state):
        for k, v in state.iteritems():
            setattr(self, k, v)
    
    def intersect(self, qry):
        """Find all intervals intersecting the given interval
        
        Keyword arguments:
        qry -- query interval
        """
        res = []
        stk = [(0, len(self.ivls))]
        while len(stk) > 0:
            lo, hi = stk.pop()
            mid = (hi + lo) / 2
            ivl = self.ivls[mid]
            stop = self.stops[mid]
            if slicetools.overlaps(qry, ivl):
                res.append(ivl)
            if lo != mid and qry.start < stop:
                stk.append((lo, mid))
            if mid + 1 < hi and ivl.start < qry.stop:
                stk.append((mid + 1, hi))
        return res
    
    def _refresh(self, lo=None, hi=None):
        """Refresh the maximum stop value for of the subtree at all nodes.
        
        Keyword variables:
        lo -- lower bound of the array/tree
        hi -- upper bound of the array/tree
        """
        lo = 0 if lo is None else lo
        hi = len(self.ivls) if hi is None else hi
        mid = (hi + lo) / 2
        
        if lo == mid:
            stop = self.ivls[mid].stop
        elif mid + 1 == hi:
            stop = max(self._refresh(lo, mid), self.ivls[mid].stop)
        else:
            stop = max(self._refresh(lo, mid), self._refresh(mid + 1, hi))
        self.stops[mid] = stop
        return stop
