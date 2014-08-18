from ebias.feature import Feature

class IterateVariants(Feature):
    
    IN = ['variant_iterator']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, variant_iterator):
        v = variant_iterator.next()
        print 'w:', v.chr, v.pos
        return variant_iterator.next()

class GetVariantByPosition(Feature):
    
    IN = ['variant_set', 'genomic_position']
    OUT = ['variant', 'genomic_position']

    def calculate(self, variant_set, genomic_position):
        return variant_set[genomic_position]

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
