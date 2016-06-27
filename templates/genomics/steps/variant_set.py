from sofia.step import Step


class GetVariantByVariant(Step):
    
    IN = ['variant', 'variant_set']
    OUT = ['variant']
    
    def run(self, variant, variant_set):
        #TODO: check matched variants
        variant_set = variant_set[0]
        for variant_ in variant:
            if variant_ is None:
                yield None
            try:
                overlap = variant_set.fetch(variant_.chr, variant_.pos, variant_.pos + 1)
            except ValueError:
                yield None
            hits = [o for o in overlap if o.pos == variant_.pos and
                    o.ref == variant_.ref and o.alt == variant_.alt]
            if len(hits) == 0:
                yield None
            yield hits
        del variant[:]

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
        variant_set = variant_set[0]
        for interval in genomic_interval:
            if interval is None:
                yield None
            try:
                hits = variant_set.fetch(interval.chr, interval.start, interval.stop)
            except ValueError, e:
                yield None
            yield ','.join(hit.id for hit in hits)
        del genomic_interval[:]
