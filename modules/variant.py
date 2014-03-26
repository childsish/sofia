from functools import total_ordering
from lhc.tools import enum

@total_ordering
class Variant:
    
    TYPES = enum(['SNP', 'MNP', 'DEL', 'INS'])
    
    def __init__(self, ivl, alt, type=[TYPES.SNP], quality=0, genotype=None):
        """Create a variant for a given genotype at a given position
        
        :param interval ivl: the position/interval of the variation
        :param list alt: a list of the alleles found at this position. Usually one is different from the reference genomes
        """
        self.ivl = ivl
        self.alt = map(str, alt)
        self.type = type
        self.quality = quality
        self.genotype = genotype
    
    def __str__(self):
        return '%s %s %s %s'%(self.ivl, self.alt, self.type, self.genotype)

    def __eq__(self, other):
        return self.ivl == other.ivl and\
            self.alt == other.alt and\
            self.type == other.type and\
            self.genotype == other.genotype

    def __lt__(self, other):
        return self.chr < other.chr or\
            self.chr == other.chr and self.start < other.start
