from sofia_.step import Step


class GetVariantByVariant(Step):
    
    IN = ['variant_set', 'variant']
    OUT = ['variant']
    
    def calculate(self, variant_set, variant):
        #TODO: check matched variants
        if variant is None:
            return None
        try:
            overlap = variant_set.fetch(variant.chr, variant.pos, variant.pos + 1)
        except ValueError:
            return None
        hits = [o for o in overlap if o.pos == variant.pos and
                o.ref == variant.ref and o.alt == variant.alt]
        if len(hits) > 1:
            raise ValueError('Too many hits')
        elif len(hits) == 0:
            return None
        return hits[0]
