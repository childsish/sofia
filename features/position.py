from ebias.feature import Feature

class Chromosome(Feature):
    
    IN = ['genomic_position']
    OUT = ['chromosome']

    def calculate(self, genomic_position):
        return genomic_position.chr

class Position(Feature):
    
    IN = ['genomic_position']
    OUT = ['position']
    
    def calculate(self, genomic_position):
        return genomic_position.pos

    def format(self, position):
        return str(position + 1)

class Quality(Feature):

    IN = ['variant']
    OUT = ['quality']

    def calculate(self, variant):
        return variant.qual

    def format(self, quality):
        if isinstance(quality, basestring):
            return quality
        return '%.2f'%quality

class Reference(Feature):

    IN = ['variant']
    OUT = ['reference']

    def calculate(self, variant):
        return variant.ref

class Alternative(Feature):

    IN = ['variant']
    OUT = ['alternative']

    def calculate(self, variant):
        return variant.alt

class ReferenceCount(Feature):

    IN = ['variant']
    OUT = ['reference_count']

    def calculate(self, variant):
        sample = variant.samples.values()[0]
        return sample['RO'] if 'RO' in sample else 'NA'

class AlternativeCount(Feature):

    IN = ['variant']
    OUT = ['alternative_count']

    def calculate(self, variant):
        sample = variant.samples.values()[0]
        return sample['AO'] if 'AO' in sample else 'NA'

