from ebias.feature import Feature

class AccessFastaByModel(Feature):
    
    IN = ['fasta', 'gene_model']
    OUT = ['nucleotide_sequence']

    def calculate(self, fasta, gene_model):
        if gene_model is None:
            return None
        return gene_model.transcripts.values()[0].getSubSeq(fasta)

class AccessFastaByHeader(Feature):
    
    IN = ['fasta', 'header']

    def calculate(self, fasta, header):
        if header is None:
            return None
        return fasta[header]
