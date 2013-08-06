'''
Created on 06/08/2013

@author: Liam Childs
'''

class interval(object):

    def __init__(self, chromosome, fr, to, strand, context=None):
        self.chr = chromosome
        self.fr, self.to = sorted((fr, to))
        self.strand = strand
        self.context = context
    
    def __eq__(self, other):
        return self.chr == other.chr and self.fr == other.fr and self.strand == other.strand
    
    def getSubSeq(self, seq):
        return seq[self.fr:self.to]
    
    def getAbsPos(self, pos):
        pass
    
    def getRelPos(self, pos):
        pass
