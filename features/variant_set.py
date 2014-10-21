from ebias.features import Feature

class GetVariantByVariant(Feature):
    
    IN = ['variant_set', 'variant']
    OUT = ['variant']

    def calculate(self, variant_set, variant):
        variant = variant['variant']
        #TODO: check matched variants
        overlap = variant_set[variant]
        hits = [o for o in overlap if o.pos == variant.pos and\
            o.ref == variant.ref and o.alt == variant.alt]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        variant = hits[0]
        return {'variant': variant}


class GetVariantsByGeneModel(Feature):
    
    IN = ['variant_set', 'gene_model']
    OUT = ['variant']
    
    def calculate(self, variant_set, gene_model):
        return variant_set[gene_model.ivl]
