import gzip

from sofia.step import Step
try:
    from lhc.io.fasta.index import IndexedFastaSet as get_fasta_set
except ImportError:
    from lhc.io.fasta import FastaInOrderAccessSet

    def get_fasta_set(filename):
        fileobj = gzip.open(filename, 'rt') if filename.endswith('.gz') else open(filename, encoding='utf-8')
        return FastaInOrderAccessSet(fileobj)


class FastaChromosomeSequenceSet(Step):

    IN = ['fasta_file']
    OUT = ['chromosome_sequence_set']
    
    def run(self, fasta_file):
        for filename in fasta_file:
            yield get_fasta_set(filename)

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
