from sofia.step import Step

from lhc.binf.genomic_coordinate import GenomicInterval


class GetVariantByVariant(Step):
    
    IN = ['variant', 'variant_set']
    OUT = ['variant']

    def consume_input(self, input):
        copy = {
            'variant_set': input['variant_set'][0],
            'variant': input['variant'][:]
        }
        del input['variant'][:]
        return copy
    
    def run(self, variant, variant_set):
        #TODO: check matched variants
        for variant_ in variant:
            if variant_ is None:
                yield []
                continue
            try:
                overlap = variant_set[GenomicInterval(variant_, variant_ + 1)]
            except ValueError:
                yield None
                continue
            hits = [o for o in overlap if o.position == variant_.position and
                    o.data['ref'] == variant_.data['ref'] and o.data['alt'] == variant_.data['alt']]
            if len(hits) == 0:
                yield None
                continue
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

    def consume_input(self, input):
        copy = {
            'variant_set': input['variant_set'][0],
            'genomic_interval': input['genomic_interval'][:]
        }
        del input['genomic_interval'][:]
        return copy

    def run(self, variant_set, genomic_interval):
        #TODO: check matched variants
        for interval in genomic_interval:
            if interval is None:
                yield None
            try:
                hits = variant_set.fetch(interval.chr, interval.start, interval.stop)
            except ValueError as e:
                yield None
            yield ','.join(hit.id for hit in hits)
