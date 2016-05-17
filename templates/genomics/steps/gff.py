from __future__ import with_statement

import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet as IntervalSet
from lhc.interval import Interval
from lhc.io.gff.iterator import GffEntryIterator
from sofia.step import Step


class GffIterator(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature']

    def run(self, gff_file):
        with gzip.open(gff_file) if gff_file.endswith('.gz') else open(gff_file) as fileobj:
            for entry in GffEntryIterator(fileobj):
                yield entry


class GffSet(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature_set']

    def run(self, gff_file):
        with gzip.open(gff_file) if gff_file.endswith('.gz') else open(gff_file) as fileobj:
            yield IntervalSet(GffEntryIterator(fileobj), key=lambda x: Interval((x.chr, x.start), (x.chr, x.stop)))
