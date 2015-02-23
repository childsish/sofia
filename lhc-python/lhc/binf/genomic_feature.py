from genomic_coordinate import Interval
from lhc.binf.sequence import revcmp
from lhc.collections.sorted_list import SortedList


class GenomicFeature(Interval):

    __slots__ = ('chr', 'start', 'stop', 'strand', 'children', 'name', 'type', 'attr')

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
    
    def get_rel_pos(self, pos, types=None):
        if len(self.children) == 0:
            return super(GenomicFeature, self).get_rel_pos(pos)

        rel_pos = 0
        children = iter(self.children) if self.strand == '+' else reversed(self.children)
        for child in children:
            if types is not None and child.type not in types:
                continue
            if child.start <= pos < child.stop:
                return rel_pos + child.get_rel_pos(pos)
            rel_pos += len(child)
        raise IndexError('absolute position {} not contained within {}'.format(pos, self))
    
    # Sequence functions
    
    def get_sub_seq(self, seq, types=None, depth=0):
        if len(self.children) == 0:
            res = seq[self.start:self.stop]
        else:
            res = ''.join(child.get_sub_seq(seq, types, depth + 1) for child in self.children
                          if types is None or child.type in types)
        if depth == 0:
            return res if self.strand == '+' else revcmp(res)
        return res

    def __getstate__(self):
        return {
            'chr': self.chr,
            'start': self.start,
            'stop': self.stop,
            'strand': self.strand,
            'children': [child.__getstate__() for child in self.children],
            'name': self.name,
            'type': self.type,
            'attr': self.attr
        }

    def __setstate__(self, state):
        setattr(self, 'chr', state['chr'])
        setattr(self, 'start', state['start'])
        setattr(self, 'stop', state['stop'])
        setattr(self, 'strand', state['strand'])
        setattr(self, 'name', state['name'])
        setattr(self, 'type', state['type'])
        setattr(self, 'attr', state['attr'])
        setattr(self, 'children', SortedList())
        for child_state in state['children']:
            child = GenomicFeature(child_state['name'])
            child.__setstate__(child_state)
            self.children.add(child)
