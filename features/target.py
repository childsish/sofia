from modules.feature import Feature

class Chromosome(Feature):
    
    IN = ['genomic_position']
    OUT = ['chromosome']

    def calculate(self, genomic_position):
        return genomic_position.chr

class Position(Feature):
    
    IN = ['genomic_position']
    OUT = ['position']
    
    def calculate(self, genomic_position):
        return genomic_position.pos
