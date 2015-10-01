from lhc.indices import CompoundIndex, KeyIndex, IntervalIndex
from lhc.interval import Interval


class BedSet(object):
    def __init__(self, iterator):
        self.data = list(iterator)
        self.ivl_index = CompoundIndex(KeyIndex, IntervalIndex)
        for i, entry in enumerate(self.data):
            ivl = Interval(entry.start, entry.stop)
            self.ivl_index[(entry.chr, ivl)] = i

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        return [self.data[v] for k, v in self.ivl_index[(chr, Interval(start, stop))]]
