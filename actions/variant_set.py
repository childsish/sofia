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
        overlap = variant_set.get_variants_at_position(chr, pos)
        hits = [o for o in overlap if o.pos == pos and
                o.ref == variant['variant'].ref and o.alt == variant['variant'].alt]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        variant = hits[0]
        return {
            'genomic_position': {
                'chromosome_id': variant.chr,
                'chromosome_pos': variant.pos
            },
            'reference_allele': variant.ref,
            'alternate_allele': variant.alt,
            'variant_quality': variant.qual,
            'info': variant.info,
            'samples': variant.samples,
            'variant': variant
        }
