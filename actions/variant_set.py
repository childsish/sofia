from sofia_.action import Action

class GetVariantByVariant(Action):
    
    IN = ['variant_set', 'variant']
    OUT = ['variant']
    
    def calculate(self, variant_set, variant):
        #TODO: check matched variants
        if variant is None:
            return None
        chr = variant['genomic_position']['chromosome_id']
        pos = variant['genomic_position']['chromosome_pos']
        overlap = variant_set.getVariantsAtPosition(chr, pos)
        hits = [o for o in overlap if o.pos == pos and\
            o.ref == variant['variant'].ref and o.alt == variant['variant'].alt]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        variant = hits[0]
        return {'variant': variant, 'genomic_position': {
            'chromosome_id': variant.chr,
            'chromosome_pos': variant.pos
        }}


class GetVariantsByGeneModel(Action):
    
    IN = ['variant_set', 'gene_model']
    OUT = ['variant']
    
    def calculate(self, variant_set, gene_model):
        return variant_set[gene_model.ivl]
