import bisect

from sofia.step import Step, EndOfStream


class GetIntervalByPosition(Step):

    IN = ['genomic_position', 'genomic_interval']
    OUT = ['genomic_interval']

    def __init__(self):
        self.position = None
        self.intervals = []
        self.stops = []

    def run(self, ins, outs):
        position = self.position
        intervals = self.intervals
        stops = self.stops

        while len(ins.genomic_position) > 0 and len(ins.genomic_interval) > 0:
            if position is None:
                position = ins.genomic_position.pop()
            if position is EndOfStream:
                outs.genomic_interval.push(EndOfStream)
                return True

            i = 0
            while i < len(intervals) and intervals[i].stop < position:
                i += 1
            del intervals[:i]

            while position is not None and len(ins.genomic_interval) > 0:
                feature = ins.genomic_feature.peek()
                if feature is EndOfStream:
                    outs.genomic_feature.push(intervals, EndOfStream)
                    return True

                if feature.start > position:
                    if not outs.genomic_feature.push(intervals):
                        self.position = None
                        return False
                    position = None
                elif feature.stop > position:
                    index = bisect.bisect(stops, feature.stop)
                    intervals.insert(index, ins.genomic_feature.pop())
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
            'genomic_interval': ins['genomic_position']
        }
