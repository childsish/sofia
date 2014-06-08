from modules.feature import Feature

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

class CountVariantSamples(Feature):
    
    IN = ['variant']
    OUT = ['variant_count']
    
    def calculate(self, variant):
        return sum(v['GT'] != '0/0' for v in variant.samples.itervalues())
