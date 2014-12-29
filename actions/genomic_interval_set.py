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
