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
    
    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        if self.sample is not None:
            if 'Q' in variant.samples[self.sample]:
                return variant.samples[self.sample]['Q']
            return '0'
        return variant.qual

    def format(self, quality):
        if isinstance(quality, basestring):
            return quality
        return '%.2f'%quality

class VariantInfo(Feature):
    
    IN = ['variant']
    OUT = ['variant_info']
    
    def init(self, key=None):
        self.key = key
    
    def calculate(self, variant):
        if variant is None:
            return None
        if self.key is None:
            return variant.info
        return variant.info[self.key]

class VariantFormat(Feature):
    
    IN = ['variant']
    OUT = ['variant_format']

    def init(self, sample=None, key=None):
        self.sample = sample
        self.key = key

    def calculate(self, variant):
        if self.sample is None and self.key is None:
            return variant.samples
        elif self.sample is not None and self.key is None:
            return variant.sample[self.sample]
        elif self.sample is None and self.key is not None:
            return {sample: format[self.key] for\
                sample, format in variant.samples.iteritems()}
        if self.key not in variant.samples[self.sample]:
            return 'NA'
        return variant.samples[self.sample][self.key]

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
    
    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        if self.sample is None:
            return {name: int(data['RO']) if 'RO' in data else 0\
                for name, data in variant.samples.iteritems()}
        data = variant.samples[self.sample]
        return int(data['RO']) if 'RO' in data else 0

class AlternativeCount(Feature):

    IN = ['variant']
    OUT = ['alternative_count']

    def init(self, sample=None, total='f'):
        self.sample = sample
        self.total = total[0].lower() == 't'

    def calculate(self, variant):
        # TODO: Find a solution for two alt alleles
        res = {name: self._getCount(data) for name, data in\
              variant.samples.iteritems()}\
            if self.sample is None else\
              self._getCount(variant.samples[self.sample])
        return res
    
    def _getCount(self, data):
        if 'AO' not in data:
            return 0
        ao = [int(count) for count in data['AO'].split(',')]
        if self.total:
            return sum(ao)
        alleles = set(int(gt) - 1 for gt in data['GT'].split('/') if gt != '0')
        count = sum(ao[allele] for allele in alleles)
        return count

class VariantFrequency(Feature):

    IN = ['variant']
    OUT = ['variant_frequency']

    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        if self.sample is None:
            return {name: self._getFrequency(sample)\
                for name, sample in variant.samples.iteritems()}
        return self._getFrequency(variant.samples[self.sample])
    
    def format(self, entity):
        if entity is None:
            return ''
        return '%.4f'%entity

    def _getFrequency(self, sample):
        if 'AO' in sample and 'DP' in sample:
            ao = sum(int(ao) for ao in sample['AO'].split(','))
            return ao / float(sample['DP'])
        elif 'AO' in sample and 'RO' in sample:
            ao = sum(int(ao) for ao in sample['AO'].split(','))
            den = ao + float(sample['RO'])
            if den == 0:
                return 0
            return ao / (ao + float(sample['RO']))
        return None

class VariantCall(Feature):

    IN = ['variant']
    OUT = ['variant_call']

    def init(self, sample=None):
        self.sample = sample
    
    def calculate(self, variant):
        if self.sample is None:
            return {name: self._getCall(sample) for name, sample\
                in variant.samples.iteritems()}
        return self._getCall(variant.samples[self.sample])

    def _getCall(self, sample):
        if 'GT' not in sample:
            return None
        a1, a2 = sample['GT'].split('/')
        if a1 == a2:
            return 'homozygous_wildtype' if a1 == '0' else 'homozygous_mutant'
        return 'heterozygous_mutant'

