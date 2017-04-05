import gzip

from sofia.step import Step
from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.maf.iterator import MafIterator
from lhc.io.vcf.iterator import Variant


class MafSet(Step):
    """A set of variants parsed from a .vcf file
    """

    IN = ['maf_file']
    OUT = ['maf_set']

    def run(self, maf_file):
        maf_file = maf_file[0]
        with gzip.open(maf_file, 'rt') if maf_file.endswith('.gz') else open(maf_file, encoding='utf-8') as fileobj:
            yield InOrderAccessIntervalSet(MafIterator(fileobj), key=maf_key)


def maf_key(line):
    return Interval((line.chr, line.start), (line.chr, line.stop))


class GetMafByVariant(Step):

    IN = ['maf_set', 'variant']
    OUT = ['maf']

    def consume_input(self, input):
        copy = {
            'maf_set': input['maf_set'][0],
            'variant': input['variant'][:]
        }
        del input['variant'][:]
        return copy

    def run(self, maf_set, variant):
        for variant_ in variant:
            #TODO: check matched variants
            if variant_ is None:
                yield None
            try:
                overlap = maf_set.fetch(variant_.chr, variant_.pos, variant_.pos + 1)
            except ValueError:
                yield None
            hits = [o for o in overlap if o.start_position == variant_.pos and
                    o.reference_allele == variant_.ref and variant_.alt in {o.tumour_seq_allele1, o.tumour_seq_allele2}]
            if len(hits) == 0:
                yield None
            yield hits


class ConvertMafToVariant(Step):

    IN = ['maf']
    OUT = ['variant']

    def run(self, maf):
        for maf_ in maf:
            if maf_ is None:
                yield None
            if isinstance(maf_, list):
                yield [
                    Variant(m.chromosome,
                            m.start_position,
                            '.', m.reference_allele,
                            ','.join({m.tumour_seq_allele1, m.tumour_seq_allele2} - {m.reference_allele}),
                            m.score,
                            '.')
                    for m in maf_]
            yield Variant(maf_.chromosome,
                          maf_.start_position,
                          '.', maf_.reference_allele,
                          ','.join({maf_.tumour_seq_allele1, maf_.tumour_seq_allele2} - {maf_.reference_allele}),
                          maf_.score,
                          '.')
