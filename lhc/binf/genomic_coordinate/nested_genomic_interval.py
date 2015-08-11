from lhc.binf.sequence import revcmp


class NestedGenomicInterval(object):

    def __init__(self, intervals=None, chr=None, strand='+', data=None):
        self.chr = intervals[0].chr if len(intervals) > 0 and chr is None else chr
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

    def get_5p(self):
        return self.intervals[0].get_5p() if self.strand == '+' else\
            self.intervals[-1].get_5p()

    def get_3p(self):
        return self.intervals[-1].get_3p() if self.strand == '+' else\
            self.intervals[0].get_3p()
