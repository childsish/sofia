from ebias.feature import Feature

class IterateHeaderSet(Feature):
    
    IN = ['header_iterator']
    OUT = ['header']
    
    def calculate(self, header_sequence_iterator):
        return header_sequence_iterator.next()
