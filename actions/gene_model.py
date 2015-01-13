from sofia_.action import Action


class MajorTranscript(Action):
    """
    Get the major transcript of a gene model. Defined as the longest transcript (ie. most complete).
    """
    
    IN = ['gene_model']
    OUT = ['major_transcript']

    def calculate(self, gene_model):
        if gene_model is None:
            return None
        return gene_model['gene_model'].get_major_transcript()
    
    def format(self, major_transcript):
        return major_transcript.name
