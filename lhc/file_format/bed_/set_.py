from lhc.indices import Index, ExactKeyIndex, OverlappingIntervalIndex
from lhc.interval import Interval


class BedSet(object):
    def __init__(self, iterator):
        self.data = list(iterator)
        self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
        for i, entry in enumerate(self.data):
            ivl = Interval(entry.start, entry.stop)
            self.ivl_index[(entry.chr, ivl)] = i

    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            length = len(key.ref) if hasattr(key, 'ref') else 1
            ivl = Interval(key.pos, key.pos + length)
            idxs = self.ivl_index[(key.chr, ivl)]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            idxs = self.ivl_index[(key.chr, key)]
        else:
            raise NotImplementedError('Variant set random access not implemented for type: {}'.format(type(key)))
        return [self.data[v] for k, v in idxs]

    def get_intervals_at_position(self, chr, pos):
        return self.get_overlapping_intervals(chr, pos, pos + 1)

    def get_overlapping_intervals(self, chr, start, stop):
        return [self.data[v] for k, v in self.ivl_index[(chr, Interval(start, stop))]]
