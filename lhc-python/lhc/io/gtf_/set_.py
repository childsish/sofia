from lhc.indices import CompoundIndex, KeyIndex, IntervalIndex
from lhc.interval import Interval


class GtfSet(object):
    def __init__(self, iterator):
        self.key_index = KeyIndex()
        self.ivl_index = CompoundIndex(KeyIndex, IntervalIndex)
        self.data = list(iterator)
        for i, entry in enumerate(self.data):
            self.key_index[entry.name] = i
            self.ivl_index[(entry.chr, Interval(entry.start, entry.stop))] = i

    def __getitem__(self, key):
        return self.data[self.key_index[key]]

    def fetch(self, chr, start, stop):
        return [self.data[v] for k, v in self.ivl_index[chr, Interval(start, stop)]]
