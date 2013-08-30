'''
Created on 06/08/2013

@author: Liam Childs
'''

class interval(object):

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
        return self.stop > other.start and other.stop > self.start
    
    def getSubSeq(self, seq):
        return seq[self.start:self.stop]
    
    def getAbsPos(self, pos):
        pass
    
    def getRelPos(self, pos):
        pass
