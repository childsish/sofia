from ebias.feature import Feature

class GetVariantByVariant(Feature):
    
    IN = ['variant_set', 'variant']
    OUT = ['variant', 'genomic_position']

    def calculate(self, variant_set, variant):
        #TODO: check matched variants
        overlap = variant_set[variant]
        hits = [o for o in overlap if o.pos == variant.pos and\
            o.ref == variant.ref and o.alt == variant.alt]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        return hits[0]

class GetVariantsByGeneModel(Feature):
    
    IN = ['variant_set', 'gene_model']
    OUT = ['variant', 'genomic_position']
    
    def calculate(self, variant_set, gene_model):
        return variant_set[gene_model.ivl]

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
