from modules.feature import Feature
from modules.resource import Resource

class AccessVcfByPosition(Feature):
    
    IN = ['vcf', 'genomic_position']
    OUT = ['variant', 'genomic_position']

    def calculate(self, genomic_position):
        return self.data[genomic_position]

class MatchVcf(Feature):
    
    IN = ['variant']
    OUT = ['vcf_match']
    
    def calculate(self, variant):
        return variant is not None
