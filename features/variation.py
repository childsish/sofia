from collections import namedtuple
from lhc.binf.genetic_code import GeneticCodes
from lhc.binf.sequence import revcmp
from ebias.feature import Feature

class VariantType(Feature):
    
    IN = ['gene_model', 'amino_acid_variant']
    OUT = ['variant_type']
    
    def calculate(self, gene_model, amino_acid_variant):
        if gene_model is None:
            return 'intergenic'
        elif amino_acid_variant is None:
            return 'intronic'
        elif all(amino_acid_variant.ref == alt for alt in amino_acid_variant.alt):
            return 'synonymous'
        return 'non-synonymous'

CodingVariant = namedtuple('CodingVariant', ('pos', 'ref', 'alt'))

class CodingVariation(Feature):
    
    IN = ['gene_model', 'variant']
    OUT = ['coding_variant']
    
    def calculate(self, gene_model, variant):
        if gene_model is None:
            return None
        coding_position = gene_model.transcripts.values()[0].getRelPos(variant.pos)
        if coding_position is None:
            return None
        ref = variant.ref
        alt = variant.alt.split(',')
        if gene_model.ivl.strand == '-':
            ref = revcmp(ref)
            alt = map(revcmp, alt)
        return CodingVariant(coding_position, ref, alt)
    
    def format(self, entity):
        return ','.join('c.%s%s>%s'%(entity.pos + 1, entity.ref, alt) for alt in entity.alt)

CodonVariant = namedtuple('CodonVariant', ['pos', 'ref', 'alt'])

class CodonVariation(Feature):
    
    IN = ['coding_variant', 'coding_sequence']
    OUT = ['codon_variant']
    
    def calculate(self, coding_variant, coding_sequence):
        if coding_variant is None:
            return None
        pos = coding_variant.pos
        pos_in_codon = pos % 3
        codon_pos = pos - pos_in_codon
        ref = coding_variant.ref
        alts = []
        for alt in coding_variant.alt:
            seq = list(coding_sequence)
            seq[pos:pos + len(ref)] = list(alt)
            alts.append(''.join(seq[codon_pos:codon_pos + 3]))
        ref_codon = coding_sequence[codon_pos:codon_pos + 3]
        return CodonVariant(pos, ref_codon, alts)
    
    def format(self, entity):
        return ','.join('c.%s%s>%s'%(entity.pos, entity.ref, alt) for alt in entity.alt)

AminoAcidVariant = namedtuple('AminoAcidVariant', ('pos', 'ref', 'alt'))

class AminoAcidVariation(Feature):
    
    IN = ['codon_variant']
    OUT = ['amino_acid_variant']
    
    def init(self):
        self.gc = GeneticCodes().getCode(1)

    def calculate(self, codon_variant):
        if codon_variant is None:
            return None
        return AminoAcidVariant(codon_variant.pos / 3,
            self.gc.translate(codon_variant.ref),
            [self.gc.translate(alt) for alt in codon_variant.alt])
    
    def format(self, entity):
        return ','.join('%s%s%s'%(entity.ref, entity.pos + 1, alt) for alt in entity.alt)

