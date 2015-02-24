import string

from itertools import izip, repeat, islice
from operator import add
from functools import total_ordering
from bx.intervals.intersection import Intersecter, Interval as BaseInterval

def seq_revcmp(seq):
    return seq[::-1]

def str_revcmp(seq):
    m = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN',
                         'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')
    return seq.translate(m)[::-1]

@total_ordering
class Interval(object):
    """
    An range class for interval set operations
    """
    
    # Reverse complement methods for different types of sequence. Assumes
    # strings are biological sequences and uses the reverse complement. 
    # Everything else is just reversed.
    REVCMPS = {basestring: str_revcmp,
        str: str_revcmp,
        list: seq_revcmp,
        tuple: seq_revcmp}
    
    def __init__(self, fr=None, to=None, value=None, chm=None,
                 strand='+'):
        import collections
        
        self.value = value
        self.strand = strand
        self.chm = chm
        self.ivls = []
        if fr is None and to is not None:
            raise TypeError('Start must be defined if end is defined')
        elif isinstance(fr, collections.Iterable):
            if to is not None:
                raise TypeError('End must not be defined if start is iterable')
            # Reverse order if on complementary strand
            if strand == '-':
                fr = reversed(fr)
            for ivl in fr:
                if type(ivl) in (list, tuple):
                    iivl = InternalInterval(ivl[0], ivl[1], value, chm,
                     strand)
                    self.ivls.append(iivl)
                elif isinstance(ivl, Interval):
                     # Keep everything on one level
                    iivls = [Interval.copyInternalInterval(ivl, strand)\
                     for ivl in ivl.ivls]
                    self.ivls.extend(iivls)
                elif isinstance(ivl, InternalInterval):
                    iivl = Interval.copyInternalInterval(ivl, strand)
                    self.ivls.append(iivl)
                else:
                    err = 'Expected a tuple or Interval as first argument.' +\
                          ' Got: %s'
                    raise ValueError(err%type(fr[0]))
        elif to is not None:
            self.ivls.append(InternalInterval(fr, to, value, chm, strand))
        elif fr is not None:
            if isinstance(fr, InternalInterval):
                ivl = fr
            else:
                ivl = InternalInterval(fr, fr + 1, value, chm, strand)
            self.ivls.append(ivl)
        
        self.tree = Intersecter()
        if fr is not None:
            for ivl in self.ivls:
                if isinstance(ivl, Interval) and len(ivl.ivls) == 0:
                    pass
                self.tree.add_interval(ivl)
    
    def __getattr__(self, key):
        if key == 'fr':
            return self.getStart()
        elif key == 'to':
            return self.getEnd()
        raise AttributeError("'Interval' object has no attribute '%s'"%key)

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        strand = self.getStrand()
        if strand == '+':
            return 'interval(%s)'%', '.join(str(ivl) for ivl in self.ivls)
        elif strand == '-':
            return 'complement(%s)'%', '.join(str(ivl) for ivl in reversed(self.ivls))
        res = []
        for ivl in self.ivls:
            pre = {'+': 'interval', '-': 'complement'}[ivl.strand]
            res.append('%s%s'%(pre, ivl))
        return 'interval(%s)'%', '.join(res)
    
    def __eq__(self, other):
        if other is None:
            return False
        for ivl1, ivl2 in izip(self.ivls, other.ivls):
            if ivl1 != ivl2:
                return False
        return True
    
    def __lt__(self, other):
        return self.getStart() <- other.getStart()
    
    def __hash__(self):
        return hash(self.ivls)
    
    def __len__(self):
        return sum(len(ivl) for ivl in self.ivls)
    
    def __getitem__(self, key):
        return Interval(self.ivls[key])
    
    def __iter__(self):
        for ivl in self.ivls:
            yield Interval(ivl)
    
    def __contains__(self, pos):
        for ivl in self.ivls:
            if pos in ivl:
                return True
        return False
    
    def __add__(self, other):
        if len(self) == 0:
            return other
        elif len(other) == 0:
            return self
        
        return Interval(self.ivls + other.ivls)
    
    def __sub__(self, other):
        # Shortcut
        if len(self) == 0 or len(other) == 0:
            return self
        
        # Calculate the difference
        res = []
        for ivl in self.ivls:
            oth_ivls = other.tree.find(ivl.start, ivl.end)
            if len(oth_ivls) == 0:
                res.append(ivl)
                continue
            
            for oth_ivl in sorted(oth_ivls):
                left, right = ivl - oth_ivl
                if left is not None:
                    res.append(left)
                if right is None:
                    break
                ivl = right
            if right is not None:
                res.append(right)
        
        # Correct for strand
        if self.getStrand() == '-':
            res = reversed(res)
        return Interval(res, value=self.value, strand=self.strand)
    
    def __and__(self, other):
        if len(self) == 0:
            return self
        elif len(other) == 0:
            return other
        
        res = []
        for ivl in self.ivls:
            oth_ivls = other.tree.find(ivl.start, ivl.end)
            for oth_ivl in sorted(oth_ivls):
                center = ivl & oth_ivl
                res.append(center)
        return Interval(res)
    
    def __or__(self, other):
        """
        Order dependent on self order. Overlaps with other used to extend
        self intervals. Remaining other intervals appended to end.
        """
        if len(self) == 0:
            return other
        elif len(other) == 0:
            return self
        
        # Extend with self intervals and their or'ed results
        res = []
        for ivl in self.ivls:
            oth_ivls = other.tree.find(ivl.start, ivl.end)
            for oth_ivl in sorted(oth_ivls):
                left, right = ivl | oth_ivl
                ivl = left
            res.append(ivl)
        # Continue with other intervals that weren't or'ed
        for oth_ivl in other.ivls:
            ivls = self.tree.find(oth_ivl.start, oth_ivl.end)
            if len(ivls) == 0:
                res.append(oth_ivl)
        return Interval(res)

    def isEmpty(self):
        return len(self.ivls) == 0

    def overlaps(self, other):
        # Traverse smaller tree (n) and search larger tree (logm)
        if len(other) < len(self):
            self, other = other, self
        
        for ivl in self.ivls:
            oth_ivls = other.tree.find(ivl.start, ivl.end)
            if len(oth_ivls) > 0:
                return True
        return False
    
    def getAbsIdx(self, pos):
        """
        Get the index to the interval containing the position
        """
        i = 0
        while i < len(self) and len(self.ivls[i]) <= pos:
            pos -= len(self.ivls[i])
            i += 1
        
        if i == len(self.ivls):
            i -= 1
        return i
    
    def getAbsPos(self, pos):
        """
        Converts a position relative to the range to one relative to 0
        """
        res, ivl = self.getAbsPosIvl(pos)
        return res
    
    def getAbsPosIvl(self, pos):
        """
        Get position and interval at the same time
        """
        ivl = self.ivls[self.getAbsIdx(pos)]
        res = ivl.get_abs_pos(pos)
        return res, ivl
    
    def getRelIdx(self, pos, value=None):
        """
        Get the index to the interval containing the position
        """
        def isMatch(ivl):
            return (value is None or value == ivl.value) and pos in ivl
        i = 0
        while i < len(self.ivls):
            if isMatch(self.ivls[i]):
                break
            i += 1
        
        if i == len(self.ivls):
            err = 'Absolute position %d is not contained within %s'
            raise IndexError(err%(pos, self))
        
        return i
    
    def getRelPos(self, pos, value=None):
        """
        Converts a position relative to 0 to one relative to the range
        """
        res, ivl = self.getRelPosIvl(pos, value=value)
        return res
    
    def getRelPosIvl(self, pos, value=None):
        """
        Get position and interval at the same time
        """
        i = self.getRelIdx(pos, value)
        ivl = self.ivls[i]
        res = sum(len(ivl) for ivl in islice(self.ivls, i)\
            if ivl.value == value) + ivl.get_rel_pos(pos)
        return res, ivl

    def getSubSeq(self, seq, value=None):
        if value is None:
            res = [ivl.get_sub_seq(seq) for ivl in self.ivls]
        else:
            res = [ivl.get_sub_seq(seq) for ivl in self.ivls\
                if ivl.value == value]
        return reduce(add, res, type(seq)())
    
    def getStart(self):
        return self.ivls[0].getStart()
    
    def getEnd(self):
        return self.ivls[-1].getEnd()
    
    def getStrand(self):
        strand = set()
        for ivl in self.ivls:
            strand.add(ivl.strand)
        
        if len(strand) == 1:
            return list(strand)[0]
        elif strand == set('+-'):
            return 'both'
        elif len(strand) > 0:
            raise ValueError('Unrecognised strands: %s'%strand)
        return None
    
    def get5pInterval(self, fr, to=0):
        iivl = self.ivls[0]
        return Interval(iivl.get_abs_pos(fr), iivl.get_abs_pos(to),
             value=iivl.value, chm=iivl.chrom, strand=iivl.strand)
    
    def get3pInterval(self, to, fr=None):
        iivl = self.ivls[-1]
        if fr == None:
            fr = len(iivl)
        to += fr
        return Interval(iivl.get_abs_pos(fr), iivl.get_abs_pos(to),
         value=iivl.value, chm=iivl.chrom, strand=iivl.strand)
    
    @classmethod
    def registerReverseComplement(cls, typ, fn):
        cls.REVCMPS[typ] = fn
    
    @staticmethod
    def copyInternalInterval(ivl, strand):
        iivl = InternalInterval(ivl.start, ivl.end, ivl.value,
         ivl.chrom, ivl.strand)
        if strand == '-':
            iivl.switchStrand()
        return iivl

def Complement(f=None, t=None, value=None, chrom=None):
    return Interval(f, t, value, chrom, strand='-')

class InternalInterval(BaseInterval):
    def __init__(self, start, end, value=None, chrom=None, strand='+'):
        start, end = sorted((start, end))
        BaseInterval.__init__(self, start, end, value, chrom, strand)

    def __str__(self):
        return '[%d..%d)'%(self.start, self.end)
    
    def __hash__(self):
        return hash((self.start, self.end))

    def __len__(self):
        return self.end - self.start

    def __contains__(self, pos):
        return self.start <= pos and pos < self.end

    def __sub__(self, other):
        # No overlap
        if self.start > other.end or other.start > self.end:
            return [None, self]
    
        res = [None, None]
        if self.start < other.start:
            res[0] = InternalInterval(self.start, other.start, self.value,
                                      self.chrom, self.strand)
        if other.end < self.end:
            res[1] = InternalInterval(other.end, self.end, self.value,
                                      self.chrom, self.strand)
        return res

    def __and__(self, other):
        # No overlap
        if self.start > other.end or other.start > self.end:
            return None
    
        res = InternalInterval(self.start, self.end, self.value, self.chrom,
                               self.strand)
        if self.start < other.start:
            res.start = other.start
        if other.end < self.end:
            res.end = other.end
        return res

    def __or__(self, other):
        # No overlap
        if self.start > other.end or other.start > self.end:
            return [self, other]
        
        ivl = InternalInterval(other.start, other.end, self.value, self.chrom,
                               self.strand)
        res = [ivl, None]
        if self.start < other.start:
            res[0].start = self.start
        if other.end < self.end:
            res[0].end = self.end
        return res
    
    def switchStrand(self):
        self.strand = {'+': '-', '-': '+'}[self.strand]
    
    def getAbsPos(self, pos):
        if self.strand == '+':
            return self.start + pos
        elif self.strand == '-':
            return self.end - pos
        raise ValueError('Unknown strand designation: %s'%self.strand)

    def getRelPos(self, pos):
        if pos < self.start or pos >= self.end:
            err = 'Absolute position %d is not contained within %s'
            raise IndexError(err%(pos, self))
    
        if self.strand == '+':
            return pos - self.start
        elif self.strand == '-':
            return self.end - pos - 1
        raise ValueError('Unknown strand designation: %s'%self.strand)

    def getSubSeq(self, seq):
        if self.start >= 0 and self.end <= len(seq):
            res = seq[self.start:self.end]
        else:
            res = []
            if self.start < 0:
                res.append(seq[self.start%len(seq):])
                res.extend(repeat(seq, abs(self.start)/len(seq)))
            elif self.start >= 0 and self.end > len(seq):
                res.append(seq[self.start:])
            
            if self.end > len(seq):
                res.extend(repeat(seq, abs(self.end)/len(seq)))
                res.append(seq[:self.end%len(seq)])
            res = reduce(add, res)
        
        # Get reverse(-complement) if on opposite strand
        if self.strand == '-':
            res = Interval.REVCMPS[type(res)](res)
        return res

    def getStart(self):
        return {'+': self.start, '-': self.end}[self.strand]

    def getEnd(self):
        return {'+': self.end, '-': self.start}[self.strand]

try:
    import numpy
    Interval.REVCMP[numpy.ndarray] = seq_revcmp
except:
    pass
