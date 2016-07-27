from lhc.io.gff import GffEntryIterator
from lhc.filetools import SharedFile, SharedGzipFile
from sofia.step import Step, EndOfStream


class IterateGff(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature']

    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                gff_file = ins.gff_file.pop()
                if gff_file is EndOfStream:
                    outs.genomic_feature.push(EndOfStream)
                    return True
                fileobj = SharedGzipFile(gff_file) if gff_file.endswith('.gz') else SharedFile(gff_file)
                self.iterator = GffEntryIterator(fileobj)

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
