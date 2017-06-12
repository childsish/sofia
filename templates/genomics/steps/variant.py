from collections import namedtuple

from lhc.binf.sequence.reverse_complement import reverse_complement

from sofia.step import Step


class GetVariantSamples(Step):

    IN = ['variant']
    OUT = ['variant_samples']

    def run(self, variant):
        for variant_ in variant:
            res = [':'.join(variant_.format)]
            for sample in variant_.samples.values():
                res.append(':'.join(sample[key] for key in variant_.format))
            yield '\t'.join(res)


class GetNumberOfVariants(Step):

    IN = ['variant']
    OUT = ['number_of_variants']

    def run(self, variant):
        for variant_ in variant:
            yield 0 if variant_ is None else len(variant_)


class GetPosition(Step):

    IN = ['chromosome_pos']
    OUT = ['position']

    def run(self, chromosome_pos):
        for position in chromosome_pos:
            yield position + 1


class GetSubstitutionContext(Step):
    
    IN = ['variant', 'chromosome_sequence_set']
    OUT = ['substitution_context']

    def consume_input(self, input):
        copy = {
            'variant': input['variant'][:],
            'chromosome_sequence_set': input['chromosome_sequence_set'][0]
        }
        del input['variant'][:]
        return copy

    def run(self, variant, chromosome_sequence_set):
        for variant_ in variant:
            context = chromosome_sequence_set[variant_.chr][variant_.pos - 1: variant_.pos + 2]
            yield context if variant_.ref[0] in 'CT' else reverse_complement(context)


class GetSubstitutionType(Step):

    IN = ['variant']
    OUT = ['substitution_type']

    def run(self, variant):
        for variant_ in variant:
            yield '{}>{}'.format(variant_.ref, variant_.alt) if variant_.ref[0] in 'CT' else '{}>{}'.format(reverse_complement(variant_.ref), reverse_complement(variant_.alt))


class GetVariantAlleleFrequency(Step):
    
    IN = ['variant']
    OUT = ['variant_allele_frequency']

    def run(self, variant):
        for variant_ in variant:
            if variant_ is None:
                yield None
            no_run = 'AF' in variant_.info or\
                (hasattr(variant_, 'samples') and
                    any('AF' in sample for sample in variant_.samples))
            if hasattr(variant_, 'samples'):
                res = {}
                if no_run:
                    for name, sample in variant_.samples.items():
                        if sample != '.':
                            res[name] = float(sample['AF'])
                else:
                    for name, sample in variant_.samples.items():
                        if sample != '.':
                            ao = float(sample['AO'])
                            ro = float(sample['RO'])
                            res[name] = ao / (ao + ro)
                yield res
            if no_run:
                yield float(variant_.info['AF'])
            ao = float(variant_.info['AO'])
            ro = float(variant_.info['RO'])
            yield ao / (ao + ro)


class VariantEffect(namedtuple('VariantEffect', ['effects'])):
    def __str__(self):
        return ', '.join(self.effects)


class GetVariantEffect(Step):
    """
    Determines the variant type according to the sequence ontology
    (http://www.sequenceontology.org)
    """
    
    IN = ['major_transcript', 'variant', 'coding_variant', 'amino_acid_variant']
    OUT = ['variant_effect']
    
    def run(self, major_transcript, variant, coding_variant, amino_acid_variant):
        for transcript, variant_, coding_variant_, amino_acid_variant_ in zip(major_transcript, variant, coding_variant, amino_acid_variant):
            #TODO: Improve intron detection
            res = []
            if transcript is None:
                res.append('intergenic_variant')
            elif coding_variant_ is None:
                res.append('intron_variant')
            else:
                for na_alt, aa_alt, fs in zip(variant_.data['alt'], amino_acid_variant_.alt, amino_acid_variant_.fs):
                    if fs is None:
                        res.append(self._get_amino_acid_type(amino_acid_variant_.pos, amino_acid_variant_.ref, aa_alt))
                    elif len(na_alt) > len(variant_.data['ref']):
                        if (len(na_alt) - len(variant_.data['ref'])) % 3 == 0:
                            res.append('inframe_insertion')
                        else:
                            res.append('frameshift_elongation')
                    else:
                        if (len(variant_.data['ref']) - len(na_alt)) % 3 == 0:
                            res.append('inframe_deletion')
                        else:
                            res.append('frameshift_truncation')
            yield VariantEffect(res)

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

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        if len(ins['variant'] | ins['coding_variant'] | ins['amino_acid_variant']) != 1:
            raise ValueError('Conflicting sync attributes when resolving GetVariantsEffect')
        return {
            'variant_effect': ins['variant']
        }


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
        for transcript, variant_ in zip(major_transcript, variant):
            if transcript is None:
                yield None
                continue
            ref = variant_.data['ref']
            pos = variant_.position
            try:
                coding_position = transcript.get_rel_pos(pos, types={'CDS'})\
                    if transcript.strand == '+'\
                    else transcript.get_rel_pos(pos + len(ref) - 1, types={'CDS'})
            except IndexError:
                yield None
                continue
            except ValueError:
                yield None
                continue
            alt = variant_.data['alt']
            if transcript.strand == '-':
                ref = reverse_complement(ref)
                alt = list(map(reverse_complement, alt))
            yield CodingVariant(coding_position, ref, alt)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        if ins['variant'] != ins['major_transcript']:
            msg = 'major_transcript and variant have conflicting sync attributes: {} vs. {}'
            raise ValueError(msg.format(ins['major_transcript'], ins['variant']))
        return {
            'coding_variant': ins['variant']
        }


class CodonVariant(namedtuple('CodonVariant', ('pos', 'ref', 'alt', 'fs'))):
    def __str__(self):
        return ','.join('c.{}{}>{}'.format(self.pos + 1, self.ref, alt) for alt in self.alt)


class GetCodonVariant(Step):
    
    IN = ['coding_variant', 'coding_sequence', 'downstream_1000']
    OUT = ['codon_variant']
    BUFFER = 1000
    
    def run(self, coding_variant, coding_sequence, downstream_1000):
        for variant, sequence, downstream in zip(coding_variant, coding_sequence, downstream_1000):
            if variant is None or sequence is None:
                yield None
                continue
            pos = variant.pos
            ref = variant.ref
            if len(ref) == 1:
                fr = pos % 3
                to = 2 - (pos % 3)
            else:
                fr = [3, 4, 2][pos % 3]
                to = [2, 4, 3][(pos + len(ref)) % 3]
            alts = []
            fs = []
            for alt in variant.alt:
                seq = list(sequence)
                seq[pos:pos + len(ref)] = list(alt)
                alts.append(''.join(seq[pos - fr:pos + len(alt) + to]))

                d = len(ref) - len(alt)
                if d == 0:
                    fs_pos = None
                else:
                    fs_pos = 0
                    seq = downstream
                    while fs_pos < len(seq) and seq[fs_pos:fs_pos + 3] not in {'TAA', 'TAG', 'TGA'}:
                        fs_pos += 3
                fs.append(fs_pos)
            ref_codon = sequence[pos - fr:pos + len(ref) + to]
            yield CodonVariant(pos - fr, ref_codon, alts, fs)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'codon_variant': ins['coding_variant']
        }


class AminoAcidVariant(namedtuple('AminoAcidVariant', ('pos', 'ref', 'alt', 'fs'))):
    def __str__(self):
        res = []
        pos = self.pos
        ref = self.ref
        for alt, fs in zip(self.alt, self.fs):
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
                    r += 'fs*{}'.format(int(fs))
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

    def consume_input(self, input):
        copy = {
            'genetic_code': input['genetic_code'][0],
            'codon_variant': input['codon_variant'][:]
        }
        del input['codon_variant'][:]
        return copy

    def run(self, codon_variant, genetic_code):
        for variant in codon_variant:
            if variant is None:
                yield None
                continue
            alts = [None if alt is None else genetic_code.translate(alt) for alt in variant.alt]
            fs = [None if fs_ is None else fs_ / 3 for fs_ in variant.fs]
            yield AminoAcidVariant(variant.pos // 3, genetic_code.translate(variant.ref), alts, fs)

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
