import operator

from lhc import intervaltools

class AugmentedTree(object):
    """An augmented tree designed to hold intervals.
    """
    __slots__ = ('ivls', 'stops')
    
    def __init__(self, ivls):
        """ Initialise the tree with a set of intervals
        
        :param list ivls: a list of intervals to be stored. The original list will be left untouched.
        """
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
    
    def getOverlapping(self, qry):
        """Find all overlapping intervals
        
        Keyword arguments:
        :param interval qry: find intervals overlapping this interval
        """
        res = []
        stk = [(0, len(self.ivls))]
        while len(stk) > 0:
            lo, hi = stk.pop()
            mid = (hi + lo) / 2
            ivl = self.ivls[mid]
            stop = self.stops[mid]
            if intervaltools.overlaps(qry, ivl):
                res.append(ivl)
            if lo != mid and qry.start < stop:
                stk.append((lo, mid))
            if mid + 1 < hi and ivl.start < qry.stop:
                stk.append((mid + 1, hi))
        return res
    
    def _refresh(self, lo=None, hi=None):
        """Refresh the maximum stop value for of the subtree at all nodes.
        
        Keyword variables:
        :param int lo: lower bound of the array/tree
        :param int hi: upper bound of the array/tree
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
