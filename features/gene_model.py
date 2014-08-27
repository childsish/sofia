from ebias.feature import Feature

class GeneName(Feature):
    
    IN = ['gene_model']
    OUT = ['gene_name']
    
    def calculate(self, gene_model):
        if gene_model is None:
            return ''
        return gene_model.name

class MajorTranscript(Feature):
    
    IN = ['gene_model']
    OUT = ['major_transcript']

    def calculate(self, gene_model):
        if gene_model is None:
            return None
        return gene_model.getMajorTranscript()
    
    def format(self, major_transcript):
        return major_transcript.name

class GenePosition(Feature):
    
    IN = ['genomic_position', 'gene_model']
    OUT = ['gene_position']

    def calculate(self, genomic_position, gene_model):
        major_transcript = gene_model.getMajorTranscript()
        return major_transcript.getRelPos(genomic_position.pos)

    def format(self, gene_position):
        return '' if gene_position is None else str(gene_position + 1)
