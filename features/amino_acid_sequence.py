from lhc.binf.genetic_code import GeneticCodes
from ebias.feature import Feature

class GetAminoAcidSequenceFromCodingSequence(Feature):
    
    IN = ['coding_sequence']
    OUT = ['amino_acid_sequence']
    
    def init(self):
        self.gc = GeneticCodes().getCode(1)

    def calculate(self, coding_sequence):
        return self.gc.translate(coding_sequence)
