from lhc.binf.genetic_code import GeneticCodes
from modules.feature import Feature

class CodingSequenceMutation(Feature):
    
    IN = ['gene_position', 'variant']
    OUT = ['coding_sequence_mutation']
    
    def calculate(self, gene_position, variant):
        if gene_position is None:
            return None
        return (variant.ref, gene_position, variant.alt.split(','))
    
    def format(self, entity):
        return ','.join('c.%s%s>%s'%(entity[1] + 1, entity[0], alt) for alt in entity[2])

class AminoAcidMutation(Feature):
    
    IN = ['coding_sequence', 'gene_position', 'variant']
    OUT = ['amino_acid_mutation']
    
    def init(self):
        self.gc = GeneticCodes().getCode(1)

    def calculate(self, coding_sequence, gene_position, variant):
        if gene_position is None:
            return None
        position_in_codon = gene_position % 3
        codon_position_in_coding_sequence = gene_position - position_in_codon
        position_in_amino_acid_sequence = codon_position_in_coding_sequence / 3
        codon = list(coding_sequence[codon_position_in_coding_sequence:codon_position_in_coding_sequence + 3])
        aa1 = self.gc.translate(codon)
        aa2 = []
        for alt in variant.alt.split(','):
            codon[position_in_codon] = alt
            aa2.append(self.gc.translate(codon))
        return (position_in_amino_acid_sequence, aa1, aa2)
    
    def format(self, entity):
        return ','.join('%s%s%s'%(entity[1], entity[0] + 1, aa2) for aa2 in entity[2])
        
