from collections import namedtuple
from itertools import izip
from lhc.binf.genetic_code import GeneticCodes
from lhc.binf.sequence import revcmp
from ebias.features import Feature

class VariantType(Feature):
    """ Determines the variant type.
    
    Determined the variant type according to the sequence ontology
    (http://www.sequenceontology.org)
    """
    
    IN = ['major_transcript', 'variant', 'coding_variant', 'amino_acid_variant']
    OUT = ['variant_type']
    
    def calculate(self, major_transcript, variant, coding_variant, amino_acid_variant):
        variant = variant['variant']
        #TODO: Improve intron detection
        if major_transcript is None:
            return ['intergenic_variant']
        elif coding_variant is None:
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
        variant = variant['variant']
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
    
    def format(self, coding_variant):
        res = []
        pos = coding_variant.pos
        ref = coding_variant.ref
        for alt in coding_variant.alt:
            if len(coding_variant.ref) > len(alt):
                d = len(coding_variant.ref) - len(alt)
                rng = '%d'%(pos + len(ref) - 1,) if d == 1 else\
                    '%d_%d'%(pos + len(ref) - d, pos + len(ref) - 1)
                res.append('c.%sdel%s'%(rng, ref[-d - 1:-1]))
            elif len(alt) > len(coding_variant.ref):
                d = len(alt) - len(coding_variant.ref)
                typ = 'dup' if alt[-d - 1:-1] == ref[-d - 1:-1] else 'ins'
                rng = '%d'%(pos + len(alt) - 1,) if d == 1 else\
                    '%d_%d'%(pos + len(alt) - d, pos + len(alt) - 1)
                res.append('c.%s%s%s'%(rng, typ, alt[-d - 1:-1]))
            else:
                if len(ref) > 1 and ref == alt[::-1]:
                    res.append('c.%d_%dinv'%(pos + 1, pos + len(ref)))
                else:
                    res.append('c.%d%s>%s'%(pos + 1, ref, alt))
        return ','.join(res)

CodonVariant = namedtuple('CodonVariant', ['pos', 'ref', 'alt'])

class CodonVariation(Feature):
    
    IN = ['coding_variant', 'coding_sequence']
    OUT = ['codon_variant']
    
    def calculate(self, coding_variant, coding_sequence):
        if coding_variant is None:
            return None
        pos = coding_variant.pos
        ref = coding_variant.ref
        if len(ref) == 1:
            fr = pos % 3
            to = 2 - (pos % 3)
        else:
            fr = [3, 4, 2][pos % 3]
            to = [2, 4, 3][(pos + len(ref)) % 3]
        alts = []
        for alt in coding_variant.alt:
            d = abs(len(ref) - len(alt))
            if d % 3 != 0:
                alts.append(None)
            else:
                seq = list(coding_sequence)
                seq[pos:pos + len(ref)] = list(alt)
                alts.append(''.join(seq[pos - fr:pos + len(alt) + to]))
        ref_codon = coding_sequence[pos - fr:pos + len(ref) + to]
        return CodonVariant(pos - fr, ref_codon, alts)

AminoAcidVariant = namedtuple('AminoAcidVariant', ('pos', 'ref', 'alt'))

class AminoAcidVariation(Feature):
    
    IN = ['codon_variant']
    OUT = ['amino_acid_variant']

    ABBREVIATIONS = {
        'A': 'Ala', 'B': 'Asx', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu', 'F': 'Phe',
        'G': 'Gly', 'H': 'His', 'I': 'Ile', 'K': 'Lys', 'L': 'Leu', 'M': 'Met',
        'N': 'Asn', 'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser', 'T': 'Thr',
        'V': 'Val', 'W': 'Trp', 'X':   'X', 'Y': 'Tyr', 'Z': 'Glx', '*': '*'
    }
    
    def init(self, use_3code='f'):
        self.gc = GeneticCodes().getCode(1)
        self.abbreviations = self.ABBREVIATIONS if use_3code[0].lower() == 't'\
            else {name: name for name in self.ABBREVIATIONS}

    def calculate(self, codon_variant):
        if codon_variant is None:
            return None
        alts = []
        alts = [None if alt is None else self.gc.translate(alt)\
            for alt in codon_variant.alt]
        return AminoAcidVariant(codon_variant.pos / 3,
            self.gc.translate(codon_variant.ref), alts)
    
    def format(self, amino_acid_variant):
        res = []
        pos = amino_acid_variant.pos
        ref = amino_acid_variant.ref
        for alt in amino_acid_variant.alt:
            if alt is None:
                res.append('')
            elif len(amino_acid_variant.ref) > len(alt):
                d = len(amino_acid_variant.ref) - len(alt)
                rng = '%d'%(pos + len(ref) - 1,) if d == 1 else\
                    '%d_%d'%(pos + len(ref) - d, pos + len(ref) - 1)
                res.append('p.%sdel%s'%(rng, ref[-d - 1:-1]))
            elif len(alt) > len(amino_acid_variant.ref):
                d = len(alt) - len(amino_acid_variant.ref)
                typ = 'dup' if alt[-d - 1:-1] == ref[-d - 1:-1] else 'ins'
                rng = '%d'%(pos + len(alt) - 1,) if d == 1 else\
                    '%d_%d'%(pos + len(alt) - d, pos + len(alt) - 1)
                res.append('p.%s%s%s'%(rng, typ, alt[-d - 1:-1]))
            else:
                i = 0
                j = len(ref) - 1
                if ref != alt:
                    while ref[i] == alt[i]:
                        i += 1
                    while ref[j] == alt[j]:
                        j -= 1
                    j += 1
                res.append('p.%s%d%s'%(ref[i:j + 1], pos + i + 1, alt[i:j + 1]))
        return ','.join(res)

