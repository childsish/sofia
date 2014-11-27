from sofia_.features import Feature

class GeneName(Feature):
    
    IN = ['gene_model']
    OUT = ['gene_id:gene_id=hugo']
    
    def calculate(self, gene_model):
        if gene_model is None:
            return ''
        return gene_model['gene_id']

class MajorTranscript(Feature):
    
    IN = ['gene_model']
    OUT = ['major_transcript']

    def calculate(self, gene_model):
        if gene_model is None:
            return None
        return gene_model['gene_model'].getMajorTranscript()
    
    def format(self, major_transcript):
        return major_transcript.name
