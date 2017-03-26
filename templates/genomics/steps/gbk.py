import gzip

from lhc.io.gbk import GbkIterator as Iterator, GbkSequenceSet
from sofia.step import Step


class GbkIterator(Step):

    IN = ['gbk_file']
    OUT = ['genomic_interval']

    def run(self, gbk_file):
        gbk_file = gbk_file[0]
        fileobj = gzip.open(gbk_file, 'rt') if gbk_file.endswith('.gz') else open(gbk_file, encoding='utf-8')
        for entry in Iterator(fileobj):
            yield entry


class GbkSet(Step):

    IN = ['gbk_file']
    OUT = ['chromosome_sequence_set']

    def run(self, gbk_file):
        gbk_file = gbk_file[0]
        fileobj = gzip.open(gbk_file, 'rt') if gbk_file.endswith('.gz') else open(gbk_file, encoding='utf-8')
        yield GbkSequenceSet(fileobj)
