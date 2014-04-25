import string

from functools import total_ordering
from lhc.interval import Interval as BaseInterval
from lhc.tools import enum

@total_ordering
class Position(object):
    def __init__(self, chromosome, position, strand='+'):
        self.chr = chromosome
        self.pos = position
        self.strand = strand
    
    def __str__(self):
        return '%s:%s'%(self.chr, self.pos)
    
    def __eq__(self, other):
        return self.chr == other.chr and self.pos == other.pos and\
            self.strand == other.strand

    def __lt__(self, other):
        return (self.chm < other.chm) or\
            (self.chm == other.chm) and (self.pos < other.pos)
   
@total_ordering 
class Interval(BaseInterval):
    
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
        return '%s:%s-%s'%(self.chr, self.start, self.stop)
    
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
    
    def getRelPos(self, pos):
        return pos - self.start if self.strand == '+'\
            else self.stop - pos - 1
    
    def getSubSeq(self, seq):
        res = super(Interval, self).getSubSeq(seq[self.chr])
        if self.strand == '-':
            res = res.translate(Interval.REVCMP)[::-1]
        return res
