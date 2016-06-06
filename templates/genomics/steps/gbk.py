import gzip

from lhc.io.gbk import GbkIterator as Iterator, GbkSequenceSet
from sofia.step import Step


class GbkIterator(Step):

    IN = ['gbk_file']
    OUT = ['genomic_interval']

    def __init__(self):
        self.fileobj = None

    def run(self, gbk_file):
        self.fileobj = gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file)
        for entry in Iterator(self.fileobj):
            yield entry


class GbkSet(Step):

    IN = ['gbk_file']
    OUT = ['chromosome_sequence_set']

    def __init__(self):
        self.fileobj = None

    def run(self, gbk_file):
        self.fileobj = gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file)
        yield GbkSequenceSet(self.fileobj)
