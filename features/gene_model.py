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
