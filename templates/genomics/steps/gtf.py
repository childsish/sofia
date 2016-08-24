from lhc.io.gtf import GtfEntryIterator
from sofia.step import Step, EndOfStream


class IterateGtf(Step):

    IN = ['gtf_file', 'filepool']
    OUT = ['genomic_feature']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.gtf_file) > 0:
            if self.iterator is None:
                gtf_file = ins.gtf_file.pop()
                if gtf_file is EndOfStream:
                    outs.genomic_feature.push(EndOfStream)
                    return True
                filepool = ins.filepool.peek()
                self.iterator = GtfEntryIterator(filepool.open(gtf_file))

            for item in self.iterator:
                if not outs.genomic_feature.push(item):
                    return False
            self.iterator = None
        return len(ins.gtf_file) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename,
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genomic_feature': set()
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'genomic_feature': ins['gtf_file']
        }
