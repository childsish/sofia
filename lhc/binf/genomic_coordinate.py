from functools import total_ordering

@total_ordering
class Position(object):
    def __init__(self, chromosome, position):
        self.chr = chromosome
        self.pos = position
    
    def __str__(self):
        return '%s:%s'%(self.chr, self.pos)
    
    def __eq__(self, other):
        return self.chr == other.chr and self.pos == other.pos

    def __lt__(self, other):
        return (self.chm < other.chm) or\
            (self.chm == other.chm) and (self.pos < other.pos)
    
class Interval(object):
    def __init__(self, chromosome, start, stop, strand='+', context=None):
        self.chr = chromosome
        self.start, self.stop = sorted((start, stop))
        self.strand = strand
        self.context = context
    
    def __str__(self):
        return '%s:%s-%s'%(self.chr, self.start, self.stop)
    
    def __eq__(self, other):
        return self.chr == other.chr and self.start == other.start and self.strand == other.strand
    
    def isOverlapping(self, other):
        if self.chr != other.chr:
            return False
        return self.stop >= other.start and other.stop >= self.start
    
    def getSubSeq(self, seq):
        return seq[self.start:self.stop]
    
    def getAbsPos(self, pos):
        pass
    
    def getRelPos(self, pos):
        pass
