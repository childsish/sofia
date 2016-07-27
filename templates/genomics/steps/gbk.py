import gzip

from lhc.io.gbk import GbkIterator as Iterator
from sofia.step import Step, EndOfStream


class IterateGbk(Step):

    IN = ['gbk_file']
    OUT = ['genomic_interval']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                gbk_file = ins.gbk_file.pop()
                if gbk_file is EndOfStream:
                    outs.genomic_interval.push(EndOfStream)
                    return True
                fileobj = gzip.open(gbk_file) if gbk_file.endswith('.gz') else open(gbk_file)
                self.iterator = Iterator(fileobj)

            for genomic_interval in self.iterator:
                if not outs.genomic_interval.push(genomic_interval):
                    return False
            self.iterator = None
        return len(ins) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genomic_interval': set()
        }
