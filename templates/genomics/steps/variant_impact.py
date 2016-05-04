from sofia.step import Step, Resource

try:
    import pysam
    import gzip

    class ProveanMap(object):
        def __init__(self, filename):
            fhndl = gzip.open(filename)
            self.headers = {aa: i for i, aa in enumerate(fhndl.readline().split())}
            self.headers['*'] = self.headers['Del']
            fhndl.close()
            self.index = pysam.TabixFile(filename)

        def calculate(self, transcript_id, amino_acid_variant):
            pos = amino_acid_variant.pos
            parts = list(self.index.fetch(transcript_id, pos, pos + 1))[0].split()
            if len(parts) == 0:
                return None
            try:
                res = [float(parts[self.headers[alt]]) for alt in amino_acid_variant.alt]
            except Exception, e:
                res = None
            return res


    class ProveanMapStep(Resource):

        FORMAT = 'provean_map'
        OUT = ['variant_impact_calculator']

        def get_interface(self, filename):
            return ProveanMap(filename)


    class GetVariantImpact(Step):

        IN = ['transcript_id', 'amino_acid_variant', 'variant_impact_calculator']
        OUT = ['variant_impact']

        def calculate(self, transcript_id, amino_acid_variant, variant_impact_calculator):
            if None in (transcript_id, amino_acid_variant, variant_impact_calculator):
                return None
            try:
                res = variant_impact_calculator.calculate(transcript_id, amino_acid_variant)
            except ValueError, e:
                res = None
            return res


except ImportError:
    import sys
    sys.stderr.write('Unable to import pysam. PROVEAN variant impacts are unavailable.\n')
