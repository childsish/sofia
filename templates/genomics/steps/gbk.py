from __future__ import with_statement

import gzip

from lhc.io.gbk import GbkIterator as Iterator, GbkSequenceSet
from sofia.step import Step


class GbkIterator(Step):

    IN = ['gbk_file']
    OUT = ['genomic_interval']

    def run(self, gbk_file):
        with gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file) as fileobj:
            for entry in Iterator(fileobj):
                yield entry


class GbkSet(Step):

    IN = ['gbk_file']
    OUT = ['chromosome_sequence_set']

    def run(self, gbk_file):
        with gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file) as fileobj:
            yield GbkSequenceSet(fileobj)
