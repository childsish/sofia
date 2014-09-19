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
        return {name: data['RO'] if 'RO' in data else 0\
            for name, data in variant.samples.iteritems()}

class AlternativeCount(Feature):

    IN = ['variant']
    OUT = ['alternative_count']

    def calculate(self, variant):
        # TODO: Find a solution for two alt alleles
        res = {}
        for name, data in variant.samples.iteritems():
            if 'AO' not in data:
                res[name] = 0
                continue
            alleles = data['GT'].split('/')
            ao = data['AO'].split(',')
            count = sum(int(ao[int(allele) - 1]) for allele in alleles\
                if allele != '0')
            res[name] = count
        return res

class VariantFrequency(Feature):

    IN = ['reference_count', 'alternative_count']

    def init(self, sample=None):
        self.sample = sample

    def calculate(self, reference_count, alternative_count):
        if self.sample is None:
            return {sample: self._calculateFrequency(reference_count[sample],
                alternative_count[sample]) for sample in reference_count}
        return self._calculateFrequency(reference_count[self.sample],
            alternative_count[self.sample])
    
    def format(self, entity):
        return '%.4f'%entity

    def _calculateFrequency(self, ref, alt):
        alt = 0 if alt is None else float(alt)
        if alt == 0:
            return 0
        ref = 0 if ref is None else float(ref)
        return alt / (alt + ref)

