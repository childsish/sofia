from collections import Counter

from lhc.binf.genomic_coordinate.genomic_interval import GenomicInterval
from sofia.step import Step


class GetGenomicFeatureByPosition(Step):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def __init__(self):
        self.ttl = 0
        self.cnt = Counter()

    def consume_input(self, input):
        copy = {
            'genomic_feature_set': input['genomic_feature_set'][0],
            'genomic_position': input['genomic_position'][:]
        }
        del input['genomic_position'][:]
        return copy

    def run(self, genomic_feature_set, genomic_position):
        for position in genomic_position:
            res = None
            if position is not None:
                self.ttl += 1
                try:
                    features = genomic_feature_set[GenomicInterval(position, position + 1)]
                    if features is not None and len(features) > 0:
                        # TODO: select correct gene (currently selecting largest)
                        res = sorted(features, key=len)[-1]
                        res.name = res.data['name'].rsplit('.', 1)[0]
                except Exception as e:
                    if str(e).startswith('could not create iterator for region'):
                        self.cnt['could not create iterator for region ...'] += 1
                    else:
                        self.cnt[str(e)] += 1
            yield res

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'genomic_feature': ins['genomic_position']
        }

    def get_user_warnings(self):
        res = set()
        for error, cnt in self.cnt.items():
            frq = round(cnt / float(self.ttl), 3)
            if frq < 1:
                continue
            res.add('{}% of intersections produced error: {}'.format(frq * 100, error))
        return res


class GetGenomicFeatureByInterval(Step):
        
    IN = ['genomic_feature_set', 'genomic_interval']
    OUT = ['genomic_feature']

    def consume_input(self, input):
        copy = {
            'genomic_feature_set': input['genomic_feature_set'][0],
            'genomic_interval': input['genomic_interval'][:]
        }
        del input['genomic_interval'][:]
        return copy

    def run(self, genomic_feature_set, genomic_interval):
        #TODO: select correct gene (currently selecting largest)
        for interval in genomic_interval:
            features = genomic_feature_set.fetch(
                interval.chr,
                interval.start,
                interval.stop)
            if features is None or len(features) == 0:
                yield None
            res = sorted(features, key=len)[-1]
            res.name = res.name.rsplit('.')[0]
            yield res

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'genomic_feature': ins['genomic_interval']
        }
