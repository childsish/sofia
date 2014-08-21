from itertools import chain
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
        
        transcripts = chain.from_iterable(model.transcripts.itervalues()\
                for model in gene_model.itervalues())\
            if isinstance(gene_model, dict)\
            else gene_model.transcripts.itervalues()
        return {transcript.name: self._getCodingVariation(transcript, variant)\
            for transcript in transcripts if transcript is not None}

    def format(self, entity):
        if isinstance(entity, dict):
            res = []
            for k, v in entity.iteritems():
                if v is None:
                    continue
                res.append(';'.join('%s:c.%s%s>%s'%(k, v.pos + 1, v.ref, alt)\
                    for alt in v.alt))
            res = ','.join(res)
        else:
            res = ';'.join('c.%s%s>%s'%(entity.pos + 1, entity.ref, alt) for alt in entity.alt)
        return res

    def _getCodingVariation(self, transcript, variant):
        ref = variant.ref
        coding_position = transcript.getRelPos(variant.pos)\
            if transcript.ivl.strand == '+'\
            else transcript.getRelPos(variant.pos + len(ref) - 1)
        if coding_position is None:
            return None
        alt = variant.alt.split(',')
        if transcript.ivl.strand == '-':
            ref = revcmp(ref)
            alt = map(revcmp, alt)
        return CodingVariant(coding_position, ref, alt)
    

CodonVariant = namedtuple('CodonVariant', ['pos', 'ref', 'alt'])
    

class CodonVariation(Feature):
    
    IN = ['coding_variant', 'coding_sequence']
    OUT = ['codon_variant']
    
    def calculate(self, coding_variant, coding_sequence):
        if coding_variant is None:
            return None
        getVariant = self._getCodonVariation
        return {key: getVariant(coding_variant[key], coding_sequence[key])\
                for key in coding_variant if coding_variant[key] is not None}\
            if isinstance(coding_variant, dict)\
            else self._getCodonVariation(coding_variant, coding_sequence)
    
    def format(self, entity):
        if isinstance(entity, dict):
            res = []
            for k, v in entity.iteritems():
                if v is None:
                    continue
                res.append(';'.join('%s:c.%s%s>%s'%(k, v.pos + 1, v.ref, alt)\
                    for alt in v.alt))
            res = ','.join(res)
        else:
            res = ';'.join('c.%s%s>%s'%(entity.pos + 1, entity.ref, alt)\
                for alt in entity.alt)
        return res
    
    def _getCodonVariation(self, coding_variant, coding_sequence):
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
        

AminoAcidVariant = namedtuple('AminoAcidVariant', ('pos', 'ref', 'alt'))

class AminoAcidVariation(Feature):
    
    IN = ['codon_variant']
    OUT = ['amino_acid_variant']
    
    def init(self):
        self.gc = GeneticCodes().getCode(1)

    def calculate(self, codon_variant):
        if codon_variant is None:
            return None
        return {k: self._getAminoAcidVariation(v)\
                for k, v in codon_variant.iteritems()}\
            if isinstance(codon_variant, dict)\
            else self._getAminoAcidVariation(codon_variant)
    
    def format(self, entity):
        if isinstance(entity, dict):
            res = []
            for k, e in entity.iteritems():
                res.append(';'.join('%s:%s%s%s'%(k, e.ref, e.pos + 1, alt)\
                    for alt in e.alt))
            res = ','.join(res)
        else:
            res = ';'.join('%s%s%s'%(entity.ref, entity.pos + 1, alt)\
                for alt in entity.alt)
        return res

    def _getAminoAcidVariation(self, codon_variant):
        return AminoAcidVariant(codon_variant.pos / 3,
            self.gc.translate(codon_variant.ref),
            [self.gc.translate(alt) for alt in codon_variant.alt])

