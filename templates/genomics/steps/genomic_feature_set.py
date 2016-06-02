from collections import Counter

from sofia.step import Step


class GetGenomicFeatureByPosition(Step):
    
    IN = ['genomic_feature_set', 'genomic_position']
    OUT = ['genomic_feature']

    def __init__(self):
        self.ttl = 0
        self.cnt = Counter()

    def run(self, genomic_feature_set, genomic_position):
        if genomic_position is None:
            return None
        #TODO: select correct gene (currently selecting largest)
        self.ttl += 1
        try:
            features = genomic_feature_set.fetch(
                genomic_position.chr,
                genomic_position.pos,
                genomic_position.pos + 1)
        except Exception, e:
            if e.message.startswith('could not create iterator for region'):
                self.cnt['could not create iterator for region ...'] += 1
            else:
                self.cnt[e.message] += 1
            return None
        if features is None or len(features) == 0:
            return None
        res = sorted(features, key=len)[-1]
        res.name = res.name.rsplit('.')[0]
        return res

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
        #TODO: select correct gene (currently selecting largest)
        features = genomic_feature_set.fetch(
            genomic_interval.chr,
            genomic_interval.start,
            genomic_interval.stop)
        if features is None or len(features) == 0:
            return None
        res = sorted(features, key=len)[-1]
        res.name = res.name.rsplit('.')[0]
        return res
