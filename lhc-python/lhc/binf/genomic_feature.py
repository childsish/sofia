from genomic_coordinate import Interval
from lhc.collections.sorted_list import SortedList


class GenomicFeature(Interval):
    def __init__(self, name, type=None, interval=None, attr={}):
        if interval is None:
            super(GenomicFeature, self).__init__(None, None, None)
        else:
            super(GenomicFeature, self).__init__(interval.chr, interval.start, interval.stop, interval.strand)
        self.children = SortedList()
        self.name = name
        self.type = type
        self.attr = attr

    def __len__(self):
        if len(self.children) == 0:
            return super(GenomicFeature, self).__len__()
        return sum(len(child) for child in self.children)

    def __getitem__(self, key):
        if self.name == key:
            return self
        for child in self.children:
            res = child[key]
            if res is not None:
                return res
        return None

    # Creation functions

    def append(self, interval):
        if self.chr is None:
            self.chr = interval.chr
            self.start = interval.start
            self.stop = interval.stop
            self.strand = interval.strand
        elif self.chr != interval.chr or self.strand != interval.strand:
            raise ValueError('{} does not belong in {}'.format(interval, self))
        else:
            self.start = min(self.start, interval.start)
            self.stop = max(self.stop, interval.stop)
        self.children.add(interval)
    
    # Position functions
    
    def get_abs_pos(self, pos, partial_rel_pos=0):
        if pos < 0:
            raise IndexError('relative position {} not contained within {}'.format(pos, self))
        length = 0
        for child in self.children:
            child_length = len(child)
            if partial_rel_pos + length + child_length > pos:
                return child.get_abs_pos(pos, partial_rel_pos + length)
            length += child_length
        if length > 0:
            raise IndexError('relative position {} not contained within {}'.format(pos, self))
        return self.start + pos - partial_rel_pos
    
    def get_rel_pos(self, pos, partial_rel_pos=0):
        length = 0
        for child in self.children:
            if child.start <= pos < child.stop:
                return child.get_rel_pos(pos, partial_rel_pos + length)
            length += len(child)
        if length > 0:
            raise IndexError('absolute position {} not contained within {}'.format(pos, self))
        return partial_rel_pos + pos - self.start
    
    # Sequence functions
    
    def get_sub_seq(self, seq, valid_types=None):
        sub_seq = [child.get_sub_seq(seq, valid_types) for child in self.children]
        if len(sub_seq) == 0 and (valid_types is None or self.type in valid_types):
            return seq[self.start:self.stop]
        return ''.join(sub_seq)
