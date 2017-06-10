from sofia.step import Step

from typing import Iterable
from lhc.binf.genomic_coordinate import GenomicInterval, GenomicPosition


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
            yield genomic_interval_set[GenomicInterval(position, position + 1)]

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

    def run(self, genomic_position: Iterable[GenomicPosition], genomic_interval: Iterable[GenomicInterval]):
        for position, interval in zip(genomic_position, genomic_interval):
            if position is None or len(interval) == 0:
                yield None
            ds = []
            if isinstance(interval, list):
                for i in interval:
                    ds.append((position.get_distance_to(i.start), '5p'))
                    ds.append((position.get_distance_to(i.stop), '3p'))
            else:
                ds.append((position.get_distance_to(interval.start), '5p'))
                ds.append((position.get_distance_to(interval.stop), '3p'))

            if len(ds) > 0:
                d = sorted(ds, key=lambda x:abs(x[0]))[0]
                yield '{}{:+d}'.format(d[1], d[0])
            else:
                yield None
