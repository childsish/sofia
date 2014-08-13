from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.interval import Interval

class GtfSet(object):
    def __init__(self, iterator):
        self.key_index = ExactKeyIndex()
        self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
        self.data = list(iterator)
        for i, entry in enumerate(self.data):
            self.key_index[entry.name] = i
            self.ivl_index[(entry.ivl.chr, entry.ivl)] = i

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.data[self.key_index[key]]
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            length = len(key.ref) if hasattr(key, 'ref') else 1
            ivl = Interval(key.pos, key.pos + length)
            idxs = self.ivl_index[(key.chr, ivl)]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.ivl_index[(key.chr, key)]
        else:
            raise NotImplementedError('Gene model set random access not implemented for %s'%type(key))
        return [self.data[v] for k, v in idxs]
