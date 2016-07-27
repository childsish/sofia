from sofia.step import Step, EndOfStream
from lhc.io.fasta import FastaIterator
from lhc.filetools import SharedFile, SharedGzipFile


class IterateFasta(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_segment']
    
    def __init__(self):
        self.iterator = None

    def run(self, ins, outs):
        while len(ins) > 0:
            if self.iterator is None:
                fasta_file = ins.fasta_file.pop()
                if fasta_file is EndOfStream:
                    outs.chromosome_sequence_segment.push(EndOfStream)
                    return True
                fileobj = SharedGzipFile(fasta_file) if fasta_file.endswith('.gz') else SharedFile(fasta_file)
                self.iterator = FastaIterator(fileobj)

            for chromosome_sequence_segment in self.iterator:
                if not outs.chromosome_sequence_segment.push(chromosome_sequence_segment):
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
            'chromosome_sequence_set': set()
        }
