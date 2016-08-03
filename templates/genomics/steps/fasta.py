from lhc.filetools import SharedFile
from lhc.io.fasta import FastaIterator
from sofia.step import Step, EndOfStream


class IterateFasta(Step):

    IN = ['fasta_file', 'file_worker']
    OUT = ['chromosome_sequence_segment']
    
    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins.fasta_file) > 0:
            if self.iterator is None:
                fasta_file = ins.fasta_file.pop()
                if fasta_file is EndOfStream:
                    outs.chromosome_sequence_segment.push(EndOfStream)
                    return True
                self.iterator = FastaIterator(SharedFile(fasta_file, ins.file_worker.peek()))

            for chromosome_sequence_segment in self.iterator:
                if not outs.chromosome_sequence_segment.push(chromosome_sequence_segment):
                    return False
            self.iterator = None
        return len(ins.fasta_file) == 0

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename,
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'chromosome_sequence_set': set()
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'chromosome_sequence_segment': ins['fasta_file']
        }
