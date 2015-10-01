__author__ = 'Liam Childs'

from lhc.interval import Interval
from lhc.binf.sequence import revcmp


class GenomicInterval(Interval):
    def __init__(self, chr, start, stop, strand='+', type=None, data=None):
        """Create a genomic interval

        :param string chr: the chromosome the interval is on
        :param int start: the start position of the interval (inclusive, 0-indexed)
        :param int stop: the stop position of the interval (not inclusive)
        :param strand: the strand the interval is on
        :type strand: '+' or '-'
        """
        super(GenomicInterval, self).__init__(start, stop, data)
        self.chr = chr
        self.strand = strand
        self.type = type

    def __str__(self):
        return '{}:{!r}-{!r}'.format(self.chr, self.start, self.stop)

    def __repr__(self):
        return 'GenomicInterval({s})'.format(s=str(self))

    def __eq__(self, other):
        return self.chr == other.chr and\
            super(GenomicInterval, self).__eq__(other) and\
            self.strand == other.strand

    def __lt__(self, other):
        return self.chr < other.chr or\
            self.chr == other.chr and\
            super(GenomicInterval, self).__lt__(other)

    # Relative interval functions

    def overlaps(self, other):
        """Test if self and other overlap

        :param GenomicInterval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start < other.stop and other.start < self.stop

    def contains(self, other):
        """Test if self wholly contains

        :param GenomicInterval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start <= other.start and other.stop <= self.stop

    def touches(self, other):
        """Test if self touches (but doesn't overlap) other

        :param GenomicInterval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start == other.stop or self.stop == other.start

    # Set-like operation functions

    def union(self, other):
        ivl = super(GenomicInterval, self).union(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    def union_update(self, other, compare_strand=True):
        if self.chr != other.chr or (compare_strand and self.strand != other.strand):
            raise ValueError('can not union intervals on different chromosomes/strands')
        super(GenomicInterval, self).union_update(other)

    def intersect(self, other):
        ivl = super(GenomicInterval, self).intersect(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    def intersect_update(self, other, compare_strand=True):
        if self.chr != other.chr or (compare_strand and self.strand != other.strand):
            raise ValueError('can not intersect intervals on different chromosomes/strands')
        ivl = super(GenomicInterval, self).intersect_update(other)

    def difference(self, other):
        ivl = super(GenomicInterval, self).difference(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    # Interval arithmetic functions

    def add(self, other):
        ivl = super(GenomicInterval, self).add(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    def subtract(self, other):
        ivl = super(GenomicInterval, self).subtract(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    def multiply(self, other):
        ivl = super(GenomicInterval, self).multiply(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    def divide(self, other):
        ivl = super(GenomicInterval, self).divide(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return GenomicInterval(self.chr, ivl.start, ivl.stop, self.strand)

    # Position functions

    def get_rel_pos(self, pos):
        if pos < self.start or pos >= self.stop:
            raise ValueError('Position outside interval bounds.')
        return pos - self.start if self.strand == '+'\
            else self.stop - pos - 1

    def get_sub_seq(self, sequence_set, fr=None, to=None):
        fr = self.start if fr is None else max(self.start, fr)
        to = self.stop if to is None else min(self.stop, to)
        res = sequence_set[self.chr][fr:to]# if isinstance(sequence_set, dict) else sequence_set[fr:to]
        if self.strand == '-':
            res = revcmp(res)
        return res

    def get_5p(self):
        return self.start if self.strand == '+' else\
            self.stop

    def get_3p(self):
        return self.stop if self.strand == '+' else\
            self.start
