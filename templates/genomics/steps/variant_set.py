from sofia import Step


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
        if len(hits) == 0:
            return None
        return hits


class GetVariantIdByGenomicInterval(Step):

    IN = ['variant_set', 'genomic_interval']
    OUT = ['variant_id']

    def calculate(self, variant_set, genomic_interval):
        #TODO: check matched variants
        if genomic_interval is None:
            return None
        try:
            hits = variant_set.fetch(genomic_interval.chr, genomic_interval.start, genomic_interval.stop)
        except ValueError, e:
            return None
        return ','.join(hit.id for hit in hits)
