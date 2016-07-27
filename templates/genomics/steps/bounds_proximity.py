from collections import namedtuple
from sofia.step import Step, EndOfStream


class BoundsProximity(namedtuple('BoundsProximity', ('distance', 'end'))):
    def __str__(self):
        return '{}{:+d}'.format(self.distance, self.end)


class GetBoundsProximity(Step):

    IN = ['genomic_position', 'genomic_interval']
    OUT = ['bounds_proximity']

    def run(self, ins, outs):
        while len(ins) > 0:
            genomic_position, genomic_interval = ins.pop()
            if genomic_position is EndOfStream or genomic_interval is EndOfStream:
                outs.bounds_proximity.push(EndOfStream)
                return True

            bounds_proximity = sorted((BoundsProximity(genomic_position.pos - genomic_interval.start, '5p'),
                                       BoundsProximity(genomic_position.pos - genomic_interval.stop, '3p')),
                                      key=lambda x: abs(x[0]))[0]
            if not outs.bounds_proximity.push(bounds_proximity):
                break
        return len(ins) == 0
