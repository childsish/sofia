import gzip

from sofia.step import Step
from lhc.binf.sequence.reverse_complement import reverse_complement
try:
    import pysam

    def get_fasta_set(filename):
        return pysam.FastaFile(filename)
except ImportError:
    from lhc.io.fasta import FastaInOrderAccessSet

    def get_fasta_set(filename):
        fileobj = gzip.open(filename, 'rt') if filename.endswith('.gz') else open(filename, encoding='utf-8')
        return FastaInOrderAccessSet(fileobj)


class GetDownstream1000(Step):
    """
    Get the sequence from the given genomic position to 1000 nucleotides downstream.
    """

    IN = ['fasta_file', 'genomic_position', 'major_transcript']
    OUT = ['downstream_1000']

    def __init__(self):
        self.fasta_set = None

    def consume_input(self, input):
        copy = {
            'fasta_file': input['fasta_file'][0],
            'genomic_position': input['genomic_position'][:],
            'major_transcript': input['major_transcript'][:]
        }
        del input['genomic_position'][:]
        del input['major_transcript'][:]
        return copy
    
    def run(self, fasta_file, genomic_position, major_transcript):
        for position, transcript in zip(genomic_position, major_transcript):
            if self.fasta_set is None:
                self.fasta_set = get_fasta_set(fasta_file)
            if transcript is None:
                yield None
                continue
            chr = str(position.chromosome)
            pos = position.position
            strand = transcript.strand
            start = pos if strand == '+' else pos - 1000
            stop = pos if strand == '-' else pos + 1000
            seq = self.fasta_set.fetch(chr, start, stop)
            yield seq if strand == '+' else reverse_complement(seq)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        if ins['genomic_position'] != ins['major_transcript']:
            raise ValueError('unable to resolve sync stream')
        return {
            'downstream_1000': ins['genomic_position']
        }
