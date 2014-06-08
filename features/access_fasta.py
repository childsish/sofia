from modules.feature import Feature

class AccessFastaByModel(Feature):
    
    IN = ['fasta', 'gene_model']
    OUT = ['nucleotide_sequence']

    def calculate(self, fasta, gene_model):
        return gene_model.transcripts.values()[0].getSubSeq(fasta)

class AccessFastaByHeader(Feature):
    
    IN = ['fasta', 'header']

    def calculate(self, fasta, gene_model):
        return fasta[gene_model]
