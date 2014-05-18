from modules.feature import Feature

class GetCodingSequenceFromNucleotideSequence(Feature):
    
    IN = ['nucleotide_sequence']
    OUT = ['coding_sequence']

    def calculate(self, nucleotide_sequence):
        return nucleotide_sequence.getCodingSequence()
