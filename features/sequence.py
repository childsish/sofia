from ebias.feature import Feature

class StartCodon(Feature):

    IN = ['coding_sequence']
    OUT = ['start_codon']

    def calculate(self, coding_sequence):
        return coding_sequence[:3]

