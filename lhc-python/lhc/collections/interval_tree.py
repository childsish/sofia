import collections
import operator


class IntervalTree(collections.Iterable):
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
        lefts, rights = [], []
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

    def __iter__(self):
        if self.left:
            for l in self.left:
                yield l

        for i in self.ivls:
            yield i

        if self.right:
            for r in self.right:
                yield r

    def __getitem__(self, item):
        return self.intersect(item)
 
    def intersect(self, qry):
        """Find all overlapping intervals
        
        :param interval ivl: find intervals overlapping this interval
        """
        overlapping = [ivl for ivl in self.ivls if qry.overlaps(ivl)]\
            if self.ivls and not qry.stop < self.ivls[0].start\
            else []

        if self.left and qry.start <= self.mid:
            overlapping.extend(self.left.intersect(qry))
        if self.right and qry.stop >= self.mid:
            overlapping.extend(self.right.intersect(qry))

        return overlapping


    # pickle helpers

    __slots__ = ('ivls', 'left', 'right', 'mid')

    def __getstate__(self):
        return self.ivls, self.left, self.right, self.mid

    def __setstate__(self, state):
        for k, v in zip(self.__slots__, state):
            setattr(self, k, v)
