from ebias.features import Feature

class GetIntervalByPosition(Feature):
    
    IN = ['genomic_interval_set', 'genomic_position']
    OUT = ['genomic_interval']

    def calculate(self, genomic_interval_set, genomic_position):
        return genomic_interval_set.getIntervalsAtPosition(
            genomic_position['chromosome_id'],
            genomic_position['chromosome_pos'])
    
    def format(self, genomic_interval):
        return genomic_interval[0].name
