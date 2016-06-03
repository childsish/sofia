from sofia.step import Step


class GetVariantByVariant(Step):
    
    IN = ['variant', 'variant_set']
    OUT = ['variant']
    
    def run(self, variant, variant_set):
        #TODO: check matched variants
        if variant is None:
            yield None
        try:
            overlap = variant_set.fetch(variant.chr, variant.pos, variant.pos + 1)
        except ValueError:
            yield None
        hits = [o for o in overlap if o.pos == variant.pos and
                o.ref == variant.ref and o.alt == variant.alt]
        if len(hits) == 0:
            yield None
        yield hits

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'variant': ins['variant']
        }


class GetVariantIdByGenomicInterval(Step):

    IN = ['variant_set', 'genomic_interval']
    OUT = ['variant_id']

    def run(self, variant_set, genomic_interval):
        #TODO: check matched variants
        if genomic_interval is None:
            yield None
        try:
            hits = variant_set.fetch(genomic_interval.chr, genomic_interval.start, genomic_interval.stop)
        except ValueError, e:
            yield None
        yield ','.join(hit.id for hit in hits)
