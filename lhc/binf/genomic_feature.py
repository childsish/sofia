from genomic_coordinate import Interval
from lhc.collections.sorted_list import SortedList


class GenomicFeature(Interval):
    def __init__(self, name, type=None, interval=None, attr={}):
        if interval is None:
            super(GenomicFeature, self).__init__(None, None, None)
        else:
            super(GenomicFeature, self).__init__(interval.chr, interval.start, interval.stop, interval.strand)
        self.children = SortedList()
        self.products = []
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

    def add_child(self, feature):
        if self.chr is None:
            self.chr = feature.chr
            self.start = feature.start
            self.stop = feature.stop
            self.strand = feature.strand
        elif self.chr != feature.chr or self.strand != feature.strand:
            raise ValueError('{} does not belong in {}'.format(feature, self))
        else:
            self.start = min(self.start, feature.start)
            self.stop = max(self.stop, feature.stop)
        self.children.add(feature)

    def add_product(self, feature):
        self.products.append(feature)
    
    # Position functions
    
    def get_abs_pos(self, pos, partial_rel_pos=0):
        raise NotImplementedError()
        # if pos < 0:
        #     raise IndexError('relative position {} not contained within {}'.format(pos, self))
        # length = 0
        # for child in self.children:
        #     child_length = len(child)
        #     if partial_rel_pos + length + child_length > pos:
        #         return child.get_abs_pos(pos, partial_rel_pos + length)
        #     length += child_length
        # if length > 0:
        #     raise IndexError('relative position {} not contained within {}'.format(pos, self))
        # return self.start + pos - partial_rel_pos
    
    def get_rel_pos(self, pos):
        if len(self.children) == 0:
            return super(GenomicFeature, self).get_rel_pos(pos)

        rel_pos = 0
        children = iter(self.children) if self.strand == '+' else reversed(self.children)
        for child in children:
            if child.start <= pos < child.stop:
                return rel_pos + child.get_rel_pos(pos)
            rel_pos += len(child)
        raise IndexError('absolute position {} not contained within {}'.format(pos, self))
    
    # Sequence functions
    
    def get_sub_seq(self, seq, types=None):
        sub_seq = [child.get_sub_seq(seq, types) for child in self.children]
        if len(sub_seq) == 0 and (types is None or self.type in types):
            return seq[self.start:self.stop]
        return ''.join(sub_seq)
