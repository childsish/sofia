from lhc.filetools import SharedFile
from lhc.io.bed import BedEntryIterator
from sofia.step import Step, EndOfStream


class IterateBed(Step):

    IN = ['bed_file', 'file_worker']
    OUT = ['genomic_interval']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.bed_file) > 0:
            if self.iterator is None:
                bed_file = ins.bed_file.pop()
                if bed_file is EndOfStream:
                    outs.variant.push(EndOfStream)
                    return True
                self.iterator = BedEntryIterator(SharedFile(bed_file, ins.file_worker.peek()))

            for item in self.iterator:
                if not outs.genomic_interval.push(item):
                    return False
            self.iterator = None
        return len(ins.bed_file) == 0

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
            'genomic_interval': ins['bed_file']
        }
