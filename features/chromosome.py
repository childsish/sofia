from modules.feature import Feature

class Chromosome(Feature):
    
    NAME = 'chr'
    
    def calculate(self, target):
        return target.chr
