from lhc.io.gbk import GbkIterator
from sofia.step import Step, EndOfStream


class IterateGbk(Step):

    IN = ['gbk_file', 'filepool']
    OUT = ['genomic_interval']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.gbk_file) > 0:
            if self.iterator is None:
                gbk_file = ins.gbk_file.pop()
                if gbk_file is EndOfStream:
                    outs.genomic_interval.push(EndOfStream)
                    return True
                filepool = ins.filepool.peek()
                self.iterator = GbkIterator(filepool.open(gbk_file))

            for genomic_interval in self.iterator:
                if not outs.genomic_interval.push(genomic_interval):
                    return False
            self.iterator = None
        return len(ins.gbk_file) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename,
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genomic_interval': set()
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'genomic_interval': ins['gbk_file']
        }
