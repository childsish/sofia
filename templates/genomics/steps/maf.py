from __future__ import with_statement

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
        with gzip.open(maf_file) if maf_file.endswith('.gz') else open(maf_file) as fileobj:
            yield InOrderAccessIntervalSet(MafIterator(fileobj), key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))


class GetMafByVariant(Step):

    IN = ['maf_set', 'variant']
    OUT = ['maf']

    def run(self, maf_set, variant):
        #TODO: check matched variants
        if variant is None:
            return None
        try:
            overlap = maf_set.fetch(variant.chr, variant.pos, variant.pos + 1)
        except ValueError:
            return None
        hits = [o for o in overlap if o.start_position == variant.pos and
                o.reference_allele == variant.ref and variant.alt in {o.tumour_seq_allele1, o.tumour_seq_allele2}]
        if len(hits) == 0:
            return None
        return hits


class ConvertMafToVariant(Step):

    IN = ['maf']
    OUT = ['variant']

    def run(self, maf):
        if maf is None:
            return None
        if isinstance(maf, list):
            return [
                Variant(m.chromosome,
                        m.start_position,
                        '.', m.reference_allele,
                        ','.join({m.tumour_seq_allele1, m.tumour_seq_allele2} - {m.reference_allele}),
                        m.score,
                        '.')
                for m in maf]
        return Variant(maf.chromosome,
                       maf.start_position,
                       '.', maf.reference_allele,
                       ','.join({maf.tumour_seq_allele1, maf.tumour_seq_allele2} - {maf.reference_allele}),
                       maf.score,
                       '.')
