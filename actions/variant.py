from sofia_.action import Action

class Chromosome(Action):
    
    IN = ['genomic_position']
    OUT = ['chromosome']

    def calculate(self, genomic_position):
        return genomic_position['chromosome_id']

class Position(Action):
    
    IN = ['genomic_position']
    OUT = ['position']
    
    def calculate(self, genomic_position):
        return genomic_position['chromosome_pos']

    def format(self, position):
        return str(position + 1)

class Quality(Action):

    IN = ['variant']
    OUT = ['quality']
    
    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        variant = variant['variant']
        if self.sample is None:
            return variant.qual
        elif self.sample not in variant.samples or\
                'Q' not in variant.samples[self.sample]:
            return None
        return variant.samples[self.sample]['Q']

    def format(self, quality):
        if isinstance(quality, basestring):
            return quality
        return '%.2f'%quality

class VariantInfo(Action):
    
    IN = ['variant']
    OUT = ['variant_info']
    
    def init(self, key=None):
        self.key = key
    
    def calculate(self, variant):
        if variant is None:
            return None
        variant = variant['variant']
        if self.key is None:
            return variant.info
        return variant.info[self.key]

class VariantFormat(Action):
    
    IN = ['variant']
    OUT = ['variant_format']

    def init(self, sample=None, key=None):
        self.sample = sample
        self.key = key

    def calculate(self, variant):
        variant = variant['variant']
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

class Reference(Action):

    IN = ['variant']
    OUT = ['reference']

    def calculate(self, variant):
        variant = variant['variant']
        return variant.ref

class Alternative(Action):

    IN = ['variant']
    OUT = ['alternative']

    def calculate(self, variant):
        variant = variant['variant']
        return variant.alt

class ReferenceCount(Action):

    IN = ['variant']
    OUT = ['reference_count']
    
    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        variant = variant['variant']
        if self.sample is None:
            return {name: self._getCount(data)\
                for name, data in variant.samples.iteritems()}
        elif self.sample not in variant.samples:
            return None
        return self._getCount(variant.samples[self.sample])
    
    def _getCount(self, sample):
        return int(sample['RO']) if 'RO' in sample else 0

class AlternativeCount(Action):

    IN = ['variant']
    OUT = ['alternative_count']

    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        variant = variant['variant']
        # TODO: Find a solution for two alt alleles
        if self.sample is None:
            return {name: self._getCount(data) for name, data in\
                variant.samples.iteritems()}
        elif self.sample not in variant.samples:
            return None
        return self._getCount(variant.samples[self.sample])
    
    def _getCount(self, data):
        if 'AO' not in data:
            return 0
        ao = [int(count) for count in data['AO'].split(',')]
        return sum(ao)

class Depth(Action):

    IN = ['variant']
    OUT = ['depth']
    
    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        if variant is None:
            return None
        variant = variant['variant']
        if self.sample is None:
            return {sample: self._getDepth(data)\
                for sample, data in variant.samples.iteritems()}
        elif self.sample not in variant.samples:
            return None
        return self._getDepth(variant.samples[self.sample])
    
    def _getDepth(self, sample):
        if 'DP' in sample:
            return sample['DP']
        elif 'RO' in sample and 'AO' in sample:
            ao = sum(int(ao) for ao in sample['AO'].split(','))
            return ao + int(sample['RO'])
        return None

class VariantFrequency(Action):

    IN = ['variant']
    OUT = ['variant_frequency']

    def init(self, sample=None):
        self.sample = sample

    def calculate(self, variant):
        if variant is None:
            return None
        variant = variant['variant']
        if self.sample is None:
            return {name: self._getFrequency(sample)\
                for name, sample in variant.samples.iteritems()}
        elif self.sample not in variant.samples:
            return None
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

class VariantCall(Action):

    IN = ['variant']
    OUT = ['variant_call']

    def init(self, sample=None):
        self.sample = sample
    
    def calculate(self, variant):
        variant = variant['variant']
        if self.sample is None:
            return {name: self._getCall(sample) for name, sample\
                in variant.samples.iteritems()}
        elif self.sample not in variant.samples:
            return None
        return self._getCall(variant.samples[self.sample])

    def _getCall(self, sample):
        if 'GT' not in sample:
            return None
        a1, a2 = sample['GT'].split('/')
        if a1 == a2:
            return 'homozygous_reference' if a1 == '0' else 'homozygous_variant'
        return 'heterozygous_variant'
