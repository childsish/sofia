from sofia.step import Step


class GetIntervalByPosition(Step):
    
    IN = ['genomic_interval_set', 'genomic_position']
    OUT = ['genomic_interval']

    def consume_input(self, input):
        copy = {
            'genomic_interval_set': input['genomic_interval_set'][0],
            'genomic_position': input['genomic_position'][:]
        }
        del input['genomic_position'][:]
        return copy

    def run(self, genomic_interval_set, genomic_position):
        for position in genomic_position:
            yield genomic_interval_set.fetch(
                position.chr,
                position.pos,
                position.pos + 1)

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


class GetBoundsProximity(Step):

    IN = ['genomic_position', 'genomic_interval']
    OUT = ['bounds_proximity']

    def run(self, genomic_position, genomic_interval):
        for position, interval in zip(genomic_position, genomic_interval):
            if position is None or len(interval) == 0:
                yield None
            ds = []
            if isinstance(genomic_interval, list):
                for interval in genomic_interval:
                    ds.append((position.pos - interval.start, '5p'))
                    ds.append((position.pos - interval.stop, '3p'))
            else:
                ds.append((position.pos - interval.start, '5p'))
                ds.append((position.pos - interval.stop, '3p'))
            d = sorted(ds, key=lambda x:abs(x[0]))[0]
            yield '{}{:+d}'.format(d[1], d[0])
