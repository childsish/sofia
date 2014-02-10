import operator

from lhc import slicetools

class IntervalTree(object):
    __slots__ = ('ivls', 'left', 'right', 'mid')

    def __init__(self, ivls, depth=16, minbucket=64, maxbucket=512, _extent=None):
        depth -= 1
        if (depth == 0 or len(ivls) < minbucket) and len(ivls) < maxbucket:
            self.ivls = ivls
            self.left = self.right = None
            return

        if _extent is None:
            ivls.sort(key=operator.attrgetter('start'))

        left, right = (ivls[0].start, max(i.stop for i in ivls)) if _extent is None else _extent
        mid = (left + right) / 2.0
        
        self.ivls = []
        lefts, rights  = [], []
        for ivl in ivls:
            if ivl.stop < mid:
                lefts.append(ivl)
            elif ivl.start > mid:
                rights.append(ivl)
            else:
                self.ivls.append(ivl)
               
        self.left = IntervalTree(lefts, depth, _extent=(ivls[0].start, mid)) if len(lefts) > 0 else None
        self.right = IntervalTree(rights, depth, _extent=(mid, right)) if len(rights) > 0 else None
        self.mid = mid
 
    def intersect(self, qry):
        overlapping = [ivl for ivl in self.ivls if slicetools.overlaps(qry, ivl)]\
            if self.ivls and not qry.stop < self.ivls[0].start\
            else []

        if self.left and qry.start <= self.mid:
            overlapping.extend(self.left.intersect(qry))
        if self.right and qry.stop >= self.mid:
            overlapping.extend(self.right.intersect(qry))

        return overlapping

    def __iter__(self):
        if self.left:
            for l in self.left: yield l

        for i in self.ivls: yield i

        if self.right:
            for r in self.right: yield r
    
    def __getstate__(self):
        return {'ivls': self.ivls,
            'left': self.left,
            'right': self.right,
            'mid': self.mid }

    def __setstate__(self, state):
        for k, v in state.iteritems():
            setattr(self, k, v)
