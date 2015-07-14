from lhc.binf.sequence import revcmp


class NestedGenomicInterval(object):

    def __init__(self, intervals=None, strand='+', data=None):
        self.intervals = [] if intervals is None else intervals
        self.strand = strand
        self.data = data

    def __len__(self):
        return sum(len(child) for child in self.intervals)

    # Position functions
    
    def get_abs_pos(self, pos):
        intervals = self.intervals if self.strand == '+' else reversed(self.intervals)
        fr = 0
        for interval in intervals:
            length = len(interval)
            if fr <= pos < fr + length:
                return interval.get_abs_pos(pos - fr)
            fr += length
        raise IndexError('relative position {} not contained within {}'.format(pos, self))
    
    def get_rel_pos(self, pos, types=None):
        rel_pos = 0
        intervals = iter(self.intervals) if self.strand == '+' else reversed(self.intervals)
        for interval in intervals:
            if types is not None and interval.type not in types:
                continue
            if interval.start <= pos < interval.stop:
                return rel_pos + interval.get_rel_pos(pos)
            rel_pos += len(interval)
        raise IndexError('absolute position {} not contained within {}'.format(pos, self))
    
    # Sequence functions
    
    def get_sub_seq(self, sequence_set):
        res = ''.join(interval.get_sub_seq(sequence_set) for interval in self.intervals)
        return res if self.strand == '+' else revcmp(res)
