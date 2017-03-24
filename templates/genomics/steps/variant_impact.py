import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet

from sofia.step import Step


class ProveanMap(object):
    def __init__(self, filename, index):
        fhndl = gzip.open(filename, 'rt')
        self.headers = {aa: i for i, aa in enumerate(fhndl.readline().split())}
        self.headers['*'] = self.headers['Del']
        fhndl.close()
        self.index = index

    def run(self, transcript_id, amino_acid_variant):
        for id_, variant in zip(transcript_id, amino_acid_variant):
            pos = variant.pos
            parts = list(self.index.fetch(id_, pos, pos + 1))[0].split()
            if len(parts) == 0:
                yield None
            try:
                res = [float(parts[self.headers[alt]]) for alt in variant.alt]
            except Exception as e:
                res = None
            yield res


class ProveanMapStep(Step):

    IN = ['provean_map_file']
    OUT = ['variant_impact_calculator']

    def run(self, provean_map_file):
        provean_map_file = provean_map_file[0]
        fileobj = gzip.open(provean_map_file, 'rt') if provean_map_file.endswith('.gz') else provean_map_file
        it = (line.split('\t') for line in fileobj)
        yield ProveanMap(provean_map_file, InOrderAccessSet(it, key=provean_key))


def provean_key(line):
    return line[0], int(line[1]) - 1


class GetVariantImpact(Step):

    IN = ['transcript_id', 'amino_acid_variant', 'variant_impact_calculator']
    OUT = ['variant_impact']

    def consume_input(self, input):
        copy = {
            'variant_impact_calculator': input['variant_impact_calculator'][0],
            'transcript_id': input['transcript_id'][:],
            'amino_acid_variant': input['amino_acid_variant'][:]
        }
        del input['transcript_id'][:]
        del input['amino_acid_variant'][:]
        return copy

    def run(self, transcript_id, amino_acid_variant, variant_impact_calculator):
        for id_, variant in zip(transcript_id, amino_acid_variant):
            if None in (id_, variant):
                yield None
            try:
                res = variant_impact_calculator.run(id_, variant)
            except ValueError:
                res = None
            yield res
