from collections import namedtuple
from itertools import izip
from lhc.binf.genetic_code import GeneticCodes
from lhc.binf.sequence import revcmp
from ebias.feature import Feature

class VariantType(Feature):
    """ Determines the variant type.
    
    Determined the variant type according to the sequence ontology
    (http://www.sequenceontology.org)
    """
    
    IN = ['major_transcript', 'amino_acid_variant', 'variant']
    OUT = ['variant_type']
    
    def calculate(self, major_transcript, amino_acid_variant, variant):
        if major_transcript is None:
            return ['intergenic_variant']
        elif amino_acid_variant is None:
            return ['intron_variant']
        res = []
        for na_alt, aa_alt in izip(variant.alt.split(','), amino_acid_variant.alt):
            if len(na_alt) == len(variant.ref):
                res.append(self._getAminoAcidType(amino_acid_variant.pos, 
                    amino_acid_variant.ref, aa_alt))
            elif len(na_alt) > len(variant.ref):
                if (len(na_alt) - len(variant.ref)) % 3 == 0:
                    res.append('inframe_insertion')
                else:
                    res.append('frameshift_elongation')
            else:
                if (len(variant.ref) - len(na_alt)) % 3 == 0:
                    res.append('inframe_deletion')
                else:
                    res.append('frameshift_truncation')
        return res
    
    def format(self, variant_type):
        return ','.join(variant_type)

    def _getAminoAcidType(self, pos, ref, alt):
        if ref == alt:
            if pos == 0:
                return 'start_retained_variant'
            elif ref == '*':
                return 'stop_retained_variant'
            return 'synonymous_variant'
        if pos == 0:
            return 'start_lost'
        elif ref == '*':
            return 'stop_lost'
        elif alt == '*':
            return 'stop_gained'
        #TODO: split into conservative or non-conservative
        return 'missense_variant'

CodingVariant = namedtuple('CodingVariant', ('pos', 'ref', 'alt'))

class CodingVariation(Feature):
    
    IN = ['major_transcript', 'variant']
    OUT = ['coding_variant']
    
    def calculate(self, major_transcript, variant):
        if major_transcript is None:
            return None
        ref = variant.ref
        coding_position = major_transcript.getRelPos(variant.pos)\
            if major_transcript.ivl.strand == '+'\
            else major_transcript.getRelPos(variant.pos + len(ref) - 1)
        if coding_position is None:
            return None
        alt = variant.alt.split(',')
        if major_transcript.ivl.strand == '-':
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
        alts = []
        ref = coding_variant.ref
        for alt in coding_variant.alt:
            seq = list(coding_sequence)
            seq[pos:pos + len(ref)] = list(alt)
            alts.append(''.join(seq[codon_pos:codon_pos + 3]))
        ref_codon = coding_sequence[codon_pos:codon_pos + 3]
        return CodonVariant(pos, ref_codon, alts)
    
    def format(self, entity):
        return ','.join('c.%s%s>%s'%(entity.pos + 1, entity.ref, alt) for alt in entity.alt)

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

