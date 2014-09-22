from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
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
            raise NotImplementedError('Variant set random access not implemented for type: %s'%type(key))
        return [self.data[v] for k, v in idxs]

