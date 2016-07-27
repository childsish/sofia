import gzip

from lhc.io.bed import BedEntryIterator
from lhc.filetools import SharedFile
from sofia.step import Step, EndOfStream


class IterateBed(Step):

    IN = ['bed_file']
    OUT = ['genomic_interval']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        if self.iterator is None:
            bed_file = ins.bed_file.pop()
            if bed_file is EndOfStream:
                outs.variant.push(EndOfStream)
                return True
            fileobj = gzip.open(bed_file) if bed_file.endswith('.gz') else SharedFile(bed_file)
            self.iterator = BedEntryIterator(fileobj)

        for item in self.iterator:
            if not outs.genomic_interval.push(item):
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
