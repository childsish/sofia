from __future__ import with_statement

import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.gtf.iterator import GtfEntryIterator
from sofia.step import Step


class GtfIterator(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature']

    def run(self, gtf_file):
        with gzip.open(gtf_file) if gtf_file.endswith('.gz') else open(gtf_file) as fileobj:
            for entry in GtfEntryIterator(fileobj):
                if entry.type == 'gene':
                    entry.name = entry.name.rsplit('.')[0]
                    yield entry


class GtfSet(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature_set']

    def get_interface(self, gtf_file):
        with gzip.open(gtf_file) if gtf_file.endswith('.gz') else open(gtf_file) as fileobj:
            yield InOrderAccessIntervalSet(GtfEntryIterator(fileobj), key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))
