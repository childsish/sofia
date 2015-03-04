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
        try:
            overlap = variant_set.fetch(chr, pos, pos + 1)
        except ValueError:
            return None
        hits = [o for o in overlap if o.pos == pos and
                o.ref == variant['ref'] and o.alt == variant['alt']]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        return hits[0]
