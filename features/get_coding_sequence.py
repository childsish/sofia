from lhc.binf.genetic_code import GeneticCodes
from ebias.feature import Feature

class GetCodingSequenceFromNucleotideSequence(Feature):
    
    IN = ['nucleotide_sequence']
    OUT = ['coding_sequence']
    
    def init(self):
        self.gc = GeneticCodes().getCode(1)

    def calculate(self, nucleotide_sequence):
        return nucleotide_sequence

class GetStartCodon(Feature):
    
    IN = ['coding_sequence']
    OUT = ['start_codon']
    
    def calculate(self, coding_sequence):
        return coding_sequence[:3]

class GetStopCodon(Feature):
    
    IN = ['coding_sequence']
    OUT = ['start_codon']
    
    def calculate(self, coding_sequence):
        return coding_sequence[-3:]

class GetCodingSequenceLength(Feature):
    
    IN = ['coding_sequence']
    OUT = ['coding_sequence_length']
    
    def calculate(self, coding_sequence):
        return len(coding_sequence)
