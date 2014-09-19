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
    
    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['gene_sequence']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set)

class GetGeneSequenceByHeader(Feature):
    
    IN = ['gene_sequence_set', 'header']
    OUT = ['gene_sequence']

    def calculate(self, gene_sequence_set, header):
        if header is None:
            return None
        return gene_sequence_set[header]

class GetCodingSequenceByGeneModel(Feature):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set)#, type='CDS')

class GetCodingSequencebyHeader(Feature):
    
    IN = ['coding_sequence_set', 'header']
    OUT = ['coding_sequence']

    def calculate(self, coding_sequence_set, header):
        if header is None:
            return None
        return coding_sequence_set[header]

class GetProteinSequenceByHeader(Feature):
    
    IN = ['protein_sequence_set', 'header']
    OUT = ['protein_sequence']

    def calculate(self, protein_sequence_set, header):
        if header is None:
            return None
        return protein_sequence_set[header]
