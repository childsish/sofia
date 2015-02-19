import string

from functools import total_ordering
from lhc.interval import Interval as BaseInterval


@total_ordering
class Position(object):

    __slots__ = ('chr', 'pos', 'strand')

    def __init__(self, chromosome, position, strand='+'):
        self.chr = chromosome
        self.pos = position
        self.strand = strand
    
    def __str__(self):
        return '{}:{}'.format(self.chr, self.pos)
    
    def __eq__(self, other):
        return self.chr == other.chr and self.pos == other.pos and\
            self.strand == other.strand

    def __lt__(self, other):
        return (self.chm < other.chm) or\
            (self.chm == other.chm) and (self.pos < other.pos)

    def __getstate__(self):
        return {'chr': self.chr, 'pos': self.pos, 'strand': self.strand}

    def __setstate__(self, state):
        for attribute, value in state.iteritems():
            setattr(self, attribute, value)



@total_ordering
class Interval(BaseInterval):

    __slots__ = ('chr', 'start', 'stop', 'strand')
    
    REVCMP = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN',
                              'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')
    
    def __init__(self, chm, start, stop, strand='+'):
        """Create a genomic interval
        
        :param string chm: the chromosome the interval is on
        :param int start: the start position of the interval (inclusive, 0-indexed)
        :param int stop: the stop position of the interval (not inclusive)
        :param strand: the strand the interval is on
        :type strand: '+' or '-'
        """
        super(Interval, self).__init__(start, stop)
        self.chr = chm
        self.strand = strand
    
    def __str__(self):
        return '{}:{}-{}'.format(self.chr, self.start, self.stop)
    
    def __repr__(self):
        return 'GenomicInterval({s})'.format(s=str(self))
    
    def __eq__(self, other):
        return self.chr == other.chr and\
            super(Interval, self).__eq__(other) and\
            self.strand == other.strand
    
    def __lt__(self, other):
        return self.chr < other.chr or\
            self.chr == other.chr and\
            super(Interval, self).__lt__(other)
    
    # Relative interval functions

    def overlaps(self, other):
        """Test if self and other overlap

        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start < other.stop and other.start < self.stop
    
    def contains(self, other):
        """Test if self wholly contains
    
        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start <= other.start and other.stop <= self.stop
    
    def touches(self, other):
        """Test if self touches (but doesn't overlap) other

        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.chr == other.chr and self.start == other.stop or self.stop == other.start

    # Set-like operation functions

    def union(self, other):
        ivl = super(Interval, self).union(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)

    def union_update(self, other, compare_strand=True):
        if self.chr != other.chr or (compare_strand and self.strand != other.strand):
            raise ValueError('can not union intervals on different chromosomes/strands')
        super(Interval, self).union_update(other)
    
    def intersect(self, other):
        ivl = super(Interval, self).intersect(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)

    def intersect_update(self, other, compare_strand):
        if self.chr != other.chr or (compare_strand and self.strand != other.strand):
            raise ValueError('can not intersect intervals on different chromosomes/strands')
        ivl = super(Interval, self).intersect_update(other)
    
    def difference(self, other):
        ivl = super(Interval, self).difference(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)
    
    # Interval arithmetic functions
    
    def add(self, other):
        ivl = super(Interval, self).add(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)
    
    def subtract(self, other):
        ivl = super(Interval, self).subtract(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)
    
    def multiply(self, other):
        ivl = super(Interval, self).multiply(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)
    
    def divide(self, other):
        ivl = super(Interval, self).divide(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)

    # Position functions

    def get_rel_pos(self, pos):
        if pos < self.start or pos >= self.stop:
            raise ValueError('Position outside interval bounds.')
        return pos - self.start if self.strand == '+'\
            else self.stop - pos - 1
    
    def get_sub_seq(self, seq, fr=None, to=None):
        fr = self.start if fr is None else max(self.start, fr)
        to = self.stop if to is None else min(self.stop, to)
        res = seq[self.chr][fr:to]
        if self.strand == '-':
            res = res.translate(Interval.REVCMP)[::-1]
        return res

    def __getstate__(self):
        return {'chr': self.chr, 'start': self.start, 'stop': self.stop, 'strand': self.strand}

    def __setstate__(self, state):
        for attribute, value in state.iteritems():
            setattr(self, attribute, value)
