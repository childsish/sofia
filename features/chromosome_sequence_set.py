from ebias.feature import Feature

class GetCodingSequenceByGeneModel(Feature):
    
    IN = ['chromosome_sequence_set', 'gene_model']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, gene_model):
        if gene_model is None:
            return None
        return gene_model.transcripts.values()[0].getSubSeq(chromosome_sequence_set, type='CDS')
