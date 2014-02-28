from lhc.tools import enum

class Variant:
    
    TYPES = enum(['SNP', 'MNP', 'DEL', 'INS'])
    
    def __init__(self, genotype, ivl, alt, quality, allele=1, type=Variant.TYPES.SNP):
        self.genotype = genotype
        self.ivl = ivl
        self.alt = alt
        self.quality = quality
        self.allele = allele
        self.type = type
