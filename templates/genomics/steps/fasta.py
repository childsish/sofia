import gzip

from sofia.step import Step
from lhc.io.fasta.inorder_access_set import FastaInOrderAccessSet
from lhc.filetools import SharedFile


class FastaChromosomeSequenceSet(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_set']
    
    def __init__(self, fasta_file):
        self.fileobj = None
        self.fasta_file = fasta_file.pop()

    def run(self, chromosome_sequence_set):
        if self.fileobj is None:
            self.fileobj = gzip.open(self.fasta_file) if self.fasta_file.endswith('.gz') else SharedFile(self.fasta_file)
        yield FastaInOrderAccessSet(self.fileobj)

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
