from functools import total_ordering
from interval import Interval as BaseInterval
from sequence import revcmp


@total_ordering
class Position(object):
    def __init__(self, chromosome, position, strand='+'):
        """ Create a genomic position

        A genomic position is a position on a chromosome and is defined as the
        number of nucleotides from the beginning of the chromosome and the strand the position is on.

        :param chromosome: the chromosome the position is on.
        :param position: the number of nucleotides from the beginning of the chromosome.
        :param strand: the strand the position is on.
        :return: a genomic position
        """
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

    def get_upstream(self, offset):
        return self.pos - offset if self.strand == '+' else self.pos + offset

    def get_downstream(self, offset):
        return self.get_upstream(-offset)

    def get_interval(self, other):
        return Interval(self.chr, min(self.pos, other.pos), max(self.pos, other.pos), self.strand)


@total_ordering 
class Interval(BaseInterval):
    def __init__(self, chromosome, start, stop, strand='+'):
        """Create a genomic interval
        
        :param string chromosome: the chromosome the interval is on
        :param int start: the start position of the interval (inclusive, 0-indexed)
        :param int stop: the stop position of the interval (not inclusive)
        :param strand: the strand the interval is on
        :type strand: '+' or '-'
        """
        super(Interval, self).__init__(start, stop)
        self.chr = chromosome
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
    
    # Relative location functions

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
    
    def intersect(self, other):
        ivl = super(Interval, self).intersect(other)\
            if self.chr == other.chr and self.strand == other.strand else None
        return Interval(self.chr, ivl.start, ivl.stop, self.strand)
    
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

    def get_5p(self):
        pos = self.ivl.start if self.strand == '+' else\
            self.ivl.stop
        return Position(self.chr, pos, self.strand)

    def get_3p(self):
        pos = self.ivl.start if self.strand == '-' else\
            self.ivl.stop
        return Position(self.chr, pos, self.strand)
    
    def get_rel_pos(self, pos):
        return pos - self.start if self.strand == '+'\
            else self.stop - pos - 1
    
    def get_sub_seq(self, seq, fr=None, to=None):
        fr = self.start if fr is None else max(self.start, fr)
        to = self.stop if to is None else min(self.stop, to)
        res = seq[self.chr][fr:to]
        return revcmp(res) if self.strand == '-' else res
