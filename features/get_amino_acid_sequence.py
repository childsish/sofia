from modules.feature import Feature

class GetAminoAcidSequence(Feature):
    
    IN = ['coding_sequence']
    OUT = ['amino_acid_sequence']

    def calculate(self, coding_sequence):
        return coding_sequence.translate()
