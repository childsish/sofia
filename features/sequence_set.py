from ebias.feature import Feature

class GetGeneSequenceByGeneModel(Feature):
    
    IN = ['chromosome_sequence_set', 'gene_model']
    OUT = ['gene_sequence']

    def calculate(self, chromosome_sequence_set, gene_model):
        if gene_model is None:
            return None
        return gene_model.transcripts.values()[0].getSubSeq(chromosome_sequence_set)

class GetCodingSequenceByGeneModel(Feature):
    
    IN = ['chromosome_sequence_set', 'gene_model']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, gene_model):
        if gene_model is None:
            return None
        return gene_model.transcripts.values()[0].getSubSeq(chromosome_sequence_set, type='CDS')

class GetChromosomeSequence(Feature):
    
    IN = ['chromosome_sequence_set', 'header']
    OUT = ['chromosome_sequence']

    def calculate(self, chromosome_sequence_set, header):
        if header is None:
            return None
        return chromosome_sequence_set[header]

class GetGeneSequence(Feature):
    
    IN = ['gene_sequence_set', 'header']
    OUT = ['gene_sequence']

    def calculate(self, gene_sequence_set, header):
        if header is None:
            return None
        return gene_sequence_set[header]

class GetCodingSequence(Feature):
    
    IN = ['coding_sequence_set', 'header']
    OUT = ['coding_sequence']

    def calculate(self, coding_sequence_set, header):
        if header is None:
            return None
        return coding_sequence_set[header]

class GetProteinSequence(Feature):
    
    IN = ['protein_sequence_set', 'header']
    OUT = ['protein_sequence']

    def calculate(self, protein_sequence_set, header):
        if header is None:
            return None
        return protein_sequence_set[header]
