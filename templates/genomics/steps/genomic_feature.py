import bisect

from sofia.step import Step, EndOfStream


class GetGenomicFeatureByPosition(Step):
    
    IN = ['genomic_position', 'genomic_feature']
    OUT = ['genomic_feature']

    def __init__(self):
        self.position = None
        self.features = []
        self.stops = []

    def run(self, ins, outs):
        position = self.position
        features = self.features
        stops = self.stops

        while len(ins.genomic_position) > 0 and len(ins.genomic_feature) > 0:
            if position is None:
                position = ins.genomic_position.pop()
            if position is EndOfStream:
                outs.genomic_feature.push(EndOfStream)
                return True

            i = 0
            while i < len(features) and features[i].stop < position:
                i += 1
            del features[:i]

            while position is not None and len(ins.genomic_feature) > 0:
                feature = ins.genomic_feature.peek()
                if feature is EndOfStream:
                    outs.genomic_feature.push(features, EndOfStream)
                    return True

                if feature.start > position:
                    if not outs.genomic_feature.push(features):
                        self.position = None
                        return False
                    position = None
                elif feature.stop > position:
                    index = bisect.bisect(stops, feature.stop)
                    features.insert(index, ins.genomic_feature.pop())
                    stops.insert(index, feature.stop)
        self.position = position

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

    IN = ['genomic_interval', 'genomic_feature']
    OUT = ['genomic_feature']

    def __init__(self):
        self.interval = None
        self.features = []
        self.stops = []

    def run(self, ins, outs):
        interval = self.interval
        features = self.features
        stops = self.stops

        while len(ins.genomic_position) > 0 and len(ins.genomic_feature) > 0:
            if interval is None:
                interval = ins.genomic_position.pop()
            if interval is EndOfStream:
                outs.genomic_feature.push(EndOfStream)
                return True

            i = 0
            while i < len(features) and features[i].stop < interval.start:
                i += 1
            del features[:i]

            while interval is not None and len(ins.genomic_feature) > 0:
                feature = ins.genomic_feature.peek()
                if feature is EndOfStream:
                    outs.genomic_feature.push(features, EndOfStream)
                    return True

                if feature.start > interval.stop:
                    if not outs.genomic_feature.push(features):
                        self.interval = None
                        return False
                    interval = None
                elif feature.stop > interval.start:
                    index = bisect.bisect(stops, feature.stop)
                    features.insert(index, ins.genomic_feature.pop())
                    stops.insert(index, feature.stop)
        self.interval = interval
