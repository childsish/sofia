from collections import namedtuple
from itertools import izip

from lhc.binf.sequence import revcmp

from sofia.step import Step


class GetVariantSamples(Step):

    IN = ['variant']
    OUT = ['variant_samples']

    def run(self, variant):
        res = [':'.join(variant.format)]
        for sample in variant.samples.itervalues():
            res.append(':'.join(sample[key] for key in variant.format))
        return '\t'.join(res)


class GetNumberOfVariants(Step):

    IN = ['variant']
    OUT = ['number_of_variants']

    def run(self, variant):
        return 0 if variant is None else len(variant)


class GetPosition(Step):

    IN = ['chromosome_pos']
    OUT = ['position']

    def run(self, chromosome_pos):
        return chromosome_pos + 1


class GetSubstitutionContext(Step):
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['substitution_context']

    def run(self, variant, chromosome_sequence_set):
        context = chromosome_sequence_set[variant.chr][variant.pos - 1: variant.pos + 2]
        return context if variant.ref[0] in 'CT' else revcmp(context)


class GetSubstitutionType(Step):

    IN = ['variant']
    OUT = ['substitution_type']

    def run(self, variant):
        return '{}>{}'.format(variant.ref, variant.alt) if variant.ref[0] in 'CT' else '{}>{}'.format(revcmp(variant.ref), revcmp(variant.alt))


class GetVariantAlleleFrequency(Step):
    
    IN = ['variant']
    OUT = ['variant_allele_frequency']

    def run(self, variant):
        if variant is None:
            return None
        no_run = 'AF' in variant.info or\
            (hasattr(variant, 'samples') and\
                any('AF' in sample for sample in variant.samples))
        if hasattr(variant, 'samples'):
            res = {}
            if no_run:
                for name, sample in variant.samples.iteritems():
                    if sample != '.':
                        res[name] = float(sample['AF'])
            else:
                for name, sample in variant.samples.iteritems():
                    if sample != '.':
                        ao = float(sample['AO'])
                        ro = float(sample['RO'])
                        res[name] = ao / (ao + ro)
            return res
        if no_run:
            return float(variant.info['AF'])
        ao = float(variant.info['AO'])
        ro = float(variant.info['RO'])
        return ao / (ao + ro)


class GetVariantEffect(Step):
    """
    Determines the variant type according to the sequence ontology
    (http://www.sequenceontology.org)
    """
    
    IN = ['major_transcript', 'variant', 'coding_variant', 'amino_acid_variant']
    OUT = ['variant_effect']
    
    def run(self, major_transcript, variant, coding_variant, amino_acid_variant):
        #TODO: Improve intron detection
        if major_transcript is None:
            return ['intergenic_variant']
        elif coding_variant is None:
            return ['intron_variant']
        res = []
        for na_alt, aa_alt, fs in izip(variant.alt.split(','), amino_acid_variant.alt, amino_acid_variant.fs):
            if fs is None:
                res.append(self._get_amino_acid_type(amino_acid_variant.pos, amino_acid_variant.ref, aa_alt))
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

    def _get_amino_acid_type(self, pos, ref, alt):
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


class CodingVariant(namedtuple('CodingVariant', ['pos', 'ref', 'alt'])):
    def __str__(self):
        res = []
        pos = self.pos
        ref = self.ref
        for alt in self.alt:
            if len(self.ref) > len(alt):
                d = len(self.ref) - len(alt)
                rng = str(pos + len(ref) - 1,) if d == 1 else '{}_{}'.format(pos + len(ref) - d, pos + len(ref) - 1)
                res.append('c.{}del{}'.format(rng, ref[-d - 1:-1]))
            elif len(alt) > len(self.ref):
                d = len(alt) - len(self.ref)
                typ = 'dup' if alt[-d - 1:-1] == ref[-d - 1:-1] else 'ins'
                rng = str(pos + len(alt) - 1,) if d == 1 else '{}_{}'.format(pos + len(alt) - d, pos + len(alt) - 1)
                res.append('c.{}{}{}'.format(rng, typ, alt[-d - 1:-1]))
            else:
                if len(ref) > 1 and ref == alt[::-1]:
                    res.append('c.{}_{}inv'.format(pos + 1, pos + len(ref)))
                else:
                    res.append('c.{}{}>{}'.format(pos + 1, ref, alt))
        return ','.join(res)


class GetCodingVariant(Step):
    
    IN = ['major_transcript', 'variant']
    OUT = ['coding_variant']
    
    def run(self, major_transcript, variant):
        if major_transcript is None:
            return None
        ref = variant.ref
        pos = variant.pos
        try:
            coding_position = major_transcript.get_rel_pos(pos, types={'CDS'})\
                if major_transcript.strand == '+'\
                else major_transcript.get_rel_pos(pos + len(ref) - 1, types={'CDS'})
        except IndexError:
            return None
        except ValueError:
            return None
        alt = variant.alt.split(',')
        if major_transcript.strand == '-':
            ref = revcmp(ref)
            alt = map(revcmp, alt)
        return CodingVariant(coding_position, ref, alt)


class CodonVariant(namedtuple('CodonVariant', ('pos', 'ref', 'alt', 'fs'))):
    def __str__(self):
        return ','.join('c.{}{}>{}'.format(self.pos + 1, self.ref, alt) for alt in self.alt)


class GetCodonVariant(Step):
    
    IN = ['coding_variant', 'coding_sequence', 'downstream_1000']
    OUT = ['codon_variant']
    BUFFER = 1000
    
    def run(self, coding_variant, coding_sequence, downstream_1000):
        if coding_variant is None or coding_sequence is None:
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
        fs = []
        for alt in coding_variant.alt:
            seq = list(coding_sequence)
            seq[pos:pos + len(ref)] = list(alt)
            alts.append(''.join(seq[pos - fr:pos + len(alt) + to]))
            
            d = len(ref) - len(alt)
            if d == 0:
                fs_pos = None
            else:
                fs_pos = 0
                seq = downstream_1000
                while fs_pos < len(seq) and seq[fs_pos:fs_pos + 3] not in ['TAA', 'TAG', 'TGA']:
                    fs_pos += 3
            fs.append(fs_pos)
        ref_codon = coding_sequence[pos - fr:pos + len(ref) + to]
        return CodonVariant(pos - fr, ref_codon, alts, fs)


class AminoAcidVariant(namedtuple('AminoAcidVariant', ('pos', 'ref', 'alt', 'fs'))):
    def __str__(self):
        res = []
        pos = self.pos
        ref = self.ref
        for alt, fs in izip(self.alt, self.fs):
            if len(self.ref) > len(alt):
                d = len(self.ref) - len(alt)
                rng = str(pos + len(ref) - 1,) if d == 1 else '{}_{}'.format(pos + len(ref) - d, pos + len(ref) - 1)
                r = 'p.{}del{}'.format(rng, ref[-d - 1:-1])
            elif len(alt) > len(self.ref):
                d = len(alt) - len(self.ref)
                typ = 'dup' if alt[-d - 1:-1] == ref[-d - 1:-1] else 'ins'
                rng = str(pos + len(alt) - 1,) if d == 1 else '{}_{}'.format(pos + len(alt) - d, pos + len(alt) - 1)
                r = 'p.{}{}{}'.format(rng, typ, alt[-d - 1:-1])
            else:
                i = 0
                j = len(ref) - 1
                if ref != alt:
                    while ref[i] == alt[i]:
                        i += 1
                    while ref[j] == alt[j]:
                        j -= 1
                    j += 1
                r = 'p.{}{}{}'.format(ref[i:j + 1], pos + i + 1, alt[i:j + 1])
                if fs is not None:
                    r += 'fs*{}'.format(fs)
            res.append(r)
        return ','.join(res)


class GetAminoAcidVariant(Step):
    """
    Get the amino acid variant. The nomenclature defined by the Human Genome Variation Society has been largely
    adopted (www.hgvs.org/mutnomen/).
    """
    
    IN = ['codon_variant', 'genetic_code']
    OUT = ['amino_acid_variant']
    PARAMS = ['use_3code']
    
    BUFFER = 50

    ABBREVIATIONS = {
        'A': 'Ala', 'B': 'Asx', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu', 'F': 'Phe',
        'G': 'Gly', 'H': 'His', 'I': 'Ile', 'K': 'Lys', 'L': 'Leu', 'M': 'Met',
        'N': 'Asn', 'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser', 'T': 'Thr',
        'V': 'Val', 'W': 'Trp', 'X':   'X', 'Y': 'Tyr', 'Z': 'Glx', '*': '*'
    }
    
    def __init__(self, use_3code='f'):
        self.abbreviations = self.ABBREVIATIONS if use_3code[0].lower() == 't'\
            else {name: name for name in self.ABBREVIATIONS}

    def run(self, codon_variant, genetic_code):
        if codon_variant is None:
            return None
        alts = [None if alt is None else genetic_code.translate(alt) for alt in codon_variant.alt]
        fs = [None if fs_ is None else fs_ / 3 for fs_ in codon_variant.fs]
        return AminoAcidVariant(codon_variant.pos / 3, genetic_code.translate(codon_variant.ref), alts, fs)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'amino_acid_variant': ins['codon_variant']
        }
