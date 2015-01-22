from sofia_.action import Action


class GetIntervalByPosition(Action):
    
    IN = ['genomic_interval_set', 'genomic_position']
    OUT = ['genomic_interval']

    def calculate(self, genomic_interval_set, genomic_position):
        interval = genomic_interval_set.get_intervals_at_position(
            genomic_position['chromosome_id'],
            genomic_position['chromosome_pos'])
        return {
            'chromosome_id': interval[0].chr,
            'start': interval[0].start,
            'stop': interval[0].stop,
            'data': interval[0]
        }
    
    def format(self, genomic_interval):
        return genomic_interval['data'].name


class GetBoundsProximity(Action):

    IN = ['genomic_position', 'genomic_interval']
    OUT = ['bounds_proximity']

    def calculate(self, genomic_position, genomic_interval):
        if None in (genomic_position, genomic_interval):
            return None
        return abs(genomic_position['chromosome_pos'] - genomic_interval['start']),\
            abs(genomic_interval['stop'] - genomic_position['chromosome_pos']) - 1
