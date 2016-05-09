import gzip

from lhc.io.gbk import GbkIterator as Iterator, GbkSequenceSet

from sofia.step import Resource, Target


class GbkIterator(Target):

    EXT = ['.gbk', '.gbk.gz']
    FORMAT = 'gbk_file'
    OUT = ['genomic_interval']

    def get_interface(self, filename):
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return iter(Iterator(fileobj))

    def calculate(self):
        res = self.interface.next()
        while res.type != 'CDS':
            res = self.interface.next()
        return res


class GbkSet(Resource):

    EXT = ['.gbk', '.gbk.gz']
    FORMAT = 'gbk_file'
    OUT = ['chromosome_sequence_set']

    def get_interface(self, filename):
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return GbkSequenceSet(fileobj)
