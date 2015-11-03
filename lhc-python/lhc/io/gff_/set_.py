from lhc.collections import MultiDimensionMap
from lhc.interval import Interval


class GffSet(object):
    def __init__(self, iterator):
        self.key_index = MultiDimensionMap([str])
        self.ivl_index = MultiDimensionMap([str, Interval])
        self.data = list(iterator)
        for i, entry in enumerate(self.data):
            self.key_index[entry.name] = i
            self.ivl_index[(entry.chr, Interval(entry.start, entry.stop))] = i

    def __getitem__(self, key):
        return self.data[self.key_index[key]]
    
    def fetch(self, chr, start, stop):
        return [self.data[v] for v in self.ivl_index[(chr, Interval(start, stop))]]
