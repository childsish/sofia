from ebias.feature import Feature

class GetVariantByPosition(Feature):
    
    IN = ['variant_set', 'genomic_position']
    OUT = ['variant', 'genomic_position']

    def calculate(self, variant_set, genomic_position):
        return variant_set[genomic_position]

class GetVariantsByInterval(Feature):
    
    IN = ['variant_set', 'genomic_interval']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, variant_set, genomic_interval):
        return variant_set[genomic_interval]

class GetVariantsByGeneModel(Feature):
    
    IN = ['variant_set', 'gene_model']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, variant_set, gene_model):
        return variant_set[gene_model.ivl]

class MatchVariant(Feature):
    
    IN = ['variant']
    OUT = ['variant_set_match']
    
    def calculate(self, variant):
        return variant is not None

class VariantSampleCount(Feature):
    
    IN = ['variant']
    OUT = ['variant_sample_count']
    
    def calculate(self, variant):
        return sum(v['GT'] != '0/0' for v in variant.samples.itervalues())

class VariantCount(Feature):
    
    IN = ['variant']
    OUT = ['variant_count']
    
    def calculate(self, variant):
        return len(variant)
