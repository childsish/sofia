import gzip

from lhc.io.gbk import GbkIterator as Iterator, GbkSequenceSet
from sofia.step import Step


class GbkIterator(Step):

    IN = ['gbk_file']
    OUT = ['genomic_interval']

    def run(self, gbk_file):
        gbk_file = gbk_file.pop()
        fileobj = gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file)
        for entry in Iterator(fileobj):
            yield entry


class GbkSet(Step):

    IN = ['gbk_file']
    OUT = ['chromosome_sequence_set']

    def run(self, gbk_file):
        gbk_file = gbk_file.pop()
        fileobj = gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file)
        yield GbkSequenceSet(fileobj)
