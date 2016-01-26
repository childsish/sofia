from sofia_.step import Step, Resource

try:
    import pysam
    import gzip

    class ProveanMap(object):
        def __init__(self, filename):
            fhndl = gzip.open(filename)
            self.headers = fhndl.readline().split()
            fhndl.close()
            self.index = pysam.TabixFile(filename)

        def calculate(self, gene_id, amino_acid_variant):
            pos = amino_acid_variant.pos
            parts = list(self.index.fetch(gene_id, pos, pos + 1))[0].split()
            if len(parts) == 0:
                return None
            return [float(parts[self.headers.index(alt)]) for alt in amino_acid_variant.alt]


    class ProveanMapStep(Resource):

        FORMAT = 'provean_map'
        OUT = ['variant_impact_calculator']

        def get_interface(self, filename):
            return ProveanMap(filename)


    class GetVariantImpact(Step):

        IN = ['gene_id', 'amino_acid_variant', 'variant_impact_calculator']
        OUT = ['variant_impact']

        def calculate(self, gene_id, amino_acid_variant, variant_impact_calculator):
            return variant_impact_calculator.calculate(gene_id, amino_acid_variant)


except ImportError:
    import sys
    sys.stderr.write('Unable to import pysam. PROVEAN variant impacts are unavailable.')
