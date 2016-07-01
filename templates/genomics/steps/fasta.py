import gzip

from sofia.step import Step
from lhc.io.fasta.inorder_access_set import FastaInOrderAccessSet


class FastaChromosomeSequenceSet(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_set']
    
    def run(self, fasta_file):
        fasta_file = fasta_file[0]
        fileobj = gzip.open(fasta_file) if fasta_file.endswith('.gz') else open(fasta_file)
        yield FastaInOrderAccessSet(fileobj)

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
