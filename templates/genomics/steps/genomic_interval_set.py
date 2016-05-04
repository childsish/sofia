from sofia.step import Step


class GetIntervalByPosition(Step):
    
    IN = ['genomic_interval_set', 'genomic_position']
    OUT = ['genomic_interval']

    def calculate(self, genomic_interval_set, genomic_position):
        return genomic_interval_set.fetch(
            genomic_position.chr,
            genomic_position.pos,
            genomic_position.pos + 1)
    
    def format(self, genomic_interval):
        return genomic_interval.name


class GetBoundsProximity(Step):

    IN = ['genomic_position', 'genomic_interval']
    OUT = ['bounds_proximity']

    def calculate(self, genomic_position, genomic_interval):
        if genomic_position is None or len(genomic_interval) == 0:
            return None
        ds = []
        if isinstance(genomic_interval, list):
            for interval in genomic_interval:
                ds.append((genomic_position.pos - interval.start, '5p'))
                ds.append((genomic_position.pos - interval.stop, '3p'))
        else:
            ds.append((genomic_position.pos - genomic_interval.start, '5p'))
            ds.append((genomic_position.pos - genomic_interval.stop, '3p'))
        d = sorted(ds, key=lambda x:abs(x[0]))[0]
        return '{}{:+d}'.format(d[1], d[0])
