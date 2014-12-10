from sofia_.action import Action

class GeneName(Action):
    
    IN = ['gene_model']
    OUT = ['gene_id']
    
    def calculate(self, gene_model):
        if gene_model is None:
            return ''
        return gene_model['gene_id']

class MajorTranscript(Action):
    
    IN = ['gene_model']
    OUT = ['major_transcript']

    def calculate(self, gene_model):
        if gene_model is None:
            return None
        return gene_model['gene_model'].getMajorTranscript()
    
    def format(self, major_transcript):
        return major_transcript.name