from modules.feature import Feature

class GetAminoAcidMutation(Feature):
    
    IN = ['coding_sequence', 'gene_position', 'variant']
    OUT = ['amino_acid_mutation']

    def calculate(self, coding_sequence, gene_position, variant):
        codon = coding_sequence.getCodon(gene_position)
        aa1 = codon.translate()
        codon[2] = variant.alt
        aa2 = codon.translate()
        return '%s%s%s'%(aa1, gene_position / 3, aa2)
