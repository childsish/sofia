import operator

from lhc import slicetools

class AugmentedTree(object):
    __slots__ = ('ivls', 'stops')
    
    def __init__(self, ivls):
        self.ivls = sorted(ivls, key=operator.attrgetter('start'))
        self.stops = [0 for ivl in ivls]
        self.refresh()
    
    def refresh(self, lo=None, hi=None):
        lo = 0 if lo is None else lo
        hi = len(self.ivls) if hi is None else hi
        mid = (hi + lo) / 2
        
        if lo == mid:
            stop = self.ivls[mid].stop
        elif mid + 1 == hi:
            stop = max(self.refresh(lo, mid), self.ivls[mid].stop)
        else:
            stop = max(self.refresh(lo, mid), self.refresh(mid + 1, hi))
        self.stops[mid] = stop
        return stop
    
    def intersect(self, qry, lo=None, hi=None):
        lo = 0 if lo is None else lo
        hi = len(self.ivls) if hi is None else hi
        mid = (hi + lo) / 2
        
        ivl = self.ivls[mid]
        stop = self.stops[mid]
        
        print lo, mid, hi, ivl, stop
        
        left = lo != mid and qry.start < stop
        right = mid + 1 < hi and ivl.start < qry.stop
        
        res = []
        if left:
            print 'left'
            res.extend(self.intersect(qry, lo, mid))
        print qry, ivl, slicetools.overlaps(qry, ivl)
        if slicetools.overlaps(qry, ivl):
            print 'add'
            res.append(ivl)
        if right:
            print 'right'
            res.extend(self.intersect(qry, mid + 1, hi))
        print 'up'
        return res
    
    def __iter__(self):
        return iter(self.ivls)
    
    def __getstate__(self):
        return {'ivls': self.ivls,
            'stops': self.stops}
    
    def __setstate__(self, state):
        for k, v in state.iteritems():
            setattr(self, k, v)
