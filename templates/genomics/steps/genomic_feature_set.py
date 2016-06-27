from collections import Counter

from sofia.step import Step


class GetGenomicFeatureByPosition(Step):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def __init__(self):
        self.ttl = 0
        self.cnt = Counter()

    def run(self, genomic_feature_set, genomic_position):
        genomic_feature_set = genomic_feature_set[0]
        for position in genomic_position:
            if position is None:
                yield None
                raise StopIteration()
            #TODO: select correct gene (currently selecting largest)
            self.ttl += 1
            res = None
            try:
                features = genomic_feature_set.fetch(
                    position.chr,
                    position.pos,
                    position.pos + 1)
                if features is not None and len(features) > 0:
                    res = sorted(features, key=len)[-1]
                    res.name = res.name.rsplit('.')[0]
            except Exception, e:
                if e.message.startswith('could not create iterator for region'):
                    self.cnt['could not create iterator for region ...'] += 1
                else:
                    self.cnt[e.message] += 1
            yield res
        del genomic_position[:]

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
        for error, cnt in self.cnt.iteritems():
            frq = round(cnt / float(self.ttl), 3)
            if frq < 1:
                continue
            res.add('{}% of intersections produced error: {}'.format(frq * 100, error))
        return res


class GetGenomicFeatureByInterval(Step):
        
    IN = ['genomic_feature_set', 'genomic_interval']
    OUT = ['genomic_feature']

    def run(self, genomic_feature_set, genomic_interval):
        genomic_feature_set = genomic_feature_set[0]
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
        del genomic_interval[:]
