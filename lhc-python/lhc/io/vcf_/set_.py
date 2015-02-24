from lhc.indices import Index, ExactKeyIndex, OverlappingIntervalIndex
from lhc.interval import Interval


class VcfSet(object):
    def __init__(self, iterator):
        self.data = list(iterator)
        self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
        for i, variant in enumerate(self.data):
            ivl = Interval(variant.pos, variant.pos + len(variant.ref))
            self.ivl_index[(variant.chr, ivl)] = i

    def fetch(self, chr, start, stop):
        idxs = self.ivl_index[(chr, Interval(start, stop))]
        return [self.data[v] for v in idxs.itervalues()]
