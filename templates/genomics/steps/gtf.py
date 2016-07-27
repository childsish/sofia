import gzip

from lhc.io.gtf import GtfEntryIterator
from lhc.filetools import SharedFile
from sofia.step import Step, EndOfStream


class IterateGtf(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                gtf_file = ins.gtf_file.pop()
                if gtf_file is EndOfStream:
                    outs.genomic_feature.push(EndOfStream)
                    return True
                fileobj = gzip.open(gtf_file) if gtf_file.endswith('.gz') else SharedFile(gtf_file)
                self.iterator = GtfEntryIterator(fileobj)

            for item in self.iterator:
                if not outs.genomic_feature.push(item):
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
            'genomic_feature': set()
        }
