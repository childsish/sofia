from lhc.filetools import SharedFile
from lhc.io.gff import GffEntryIterator
from sofia.step import Step, EndOfStream


class IterateGff(Step):

    IN = ['gff_file', 'file_worker']
    OUT = ['genomic_feature']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.gff_file) > 0:
            if self.iterator is None:
                gff_file = ins.gff_file.pop()
                if gff_file is EndOfStream:
                    outs.genomic_feature.push(EndOfStream)
                    return True
                self.iterator = GffEntryIterator(SharedFile(gff_file, ins.file_worker.peek()))

            for item in self.iterator:
                if not outs.genomic_feature.push(item):
                    return False
            self.iterator = None
        return len(ins.gff_file) == 0

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
            'genomic_feature': ins['fasta_file']
        }
