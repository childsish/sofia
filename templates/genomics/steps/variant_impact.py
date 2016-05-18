import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet

from sofia.step import Step


class ProveanMap(object):
    def __init__(self, filename, index):
        fhndl = gzip.open(filename)
        self.headers = {aa: i for i, aa in enumerate(fhndl.readline().split())}
        self.headers['*'] = self.headers['Del']
        fhndl.close()
        self.index = index

    def run(self, transcript_id, amino_acid_variant):
        pos = amino_acid_variant.pos
        parts = list(self.index.fetch(transcript_id, pos, pos + 1))[0].split()
        if len(parts) == 0:
            return None
        try:
            res = [float(parts[self.headers[alt]]) for alt in amino_acid_variant.alt]
        except Exception, e:
            res = None
        return res


class ProveanMapStep(Step):

    IN = ['provean_map_file']
    OUT = ['variant_impact_calculator']

    def run(self, provean_map_file):
        fileobj = gzip.open(provean_map_file) if provean_map_file.endswith('.gz') else provean_map_file
        it = (line.split('\t') for line in fileobj)
        return ProveanMap(provean_map_file, InOrderAccessSet(it, key=lambda x: (x[0], int(x[1]) - 1)))


class GetVariantImpact(Step):

    IN = ['transcript_id', 'amino_acid_variant', 'variant_impact_calculator']
    OUT = ['variant_impact']

    def run(self, transcript_id, amino_acid_variant, variant_impact_calculator):
        if None in (transcript_id, amino_acid_variant, variant_impact_calculator):
            return None
        try:
            res = variant_impact_calculator.run(transcript_id, amino_acid_variant)
        except ValueError, e:
            res = None
        return res
