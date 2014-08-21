from itertools import chain
from ebias.feature import Feature

class IterateCodingSequence(Feature):
    
    IN = ['coding_sequence_iterator']
    OUT = ['coding_sequence']
    
    def calculate(self, coding_sequence_iterator):
        return coding_sequence_iterator.next()

class IterateProteinSequence(Feature):
    
    IN = ['protein_sequence_iterator']
    OUT = ['protein_sequence']
    
    def calculate(self, protein_sequence_iterator):
        return protein_sequence_iterator.next()

class GetGeneSequenceByGeneModel(Feature):
    
    IN = ['chromosome_sequence_set', 'gene_model']
    OUT = ['gene_sequence']

    def calculate(self, chromosome_sequence_set, gene_model):
        if gene_model is None:
            return None
        transcripts = chain(model.transcripts.itervalues()\
                for model in gene_model.itervalues())\
            if isinstance(gene_model, dict)\
            else gene_model.transcripts.itervalues()
        return {transcript.name: transcript.getSubSeq(chromosome_sequence_set)\
            for transcript in transcripts}

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
