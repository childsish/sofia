import gzip

from lhc.binf.sequence import revcmp
from lhc.io.fasta import FastaIterator, FastaInOrderAccessSet
from sofia.step import Step


class GetDownstream1000(Step):
    """
    Get the sequence from the given genomic position to 1000 nucleotides downstream.
    """

    IN = ['fasta_file', 'genomic_position', 'major_transcript']
    OUT = ['downstream_1000']

    def __init__(self):
        self.fasta_set = None
    
    def run(self, fasta_file, genomic_position, major_transcript):
        fasta_file = fasta_file[0]
        for position, transcript in zip(genomic_position, major_transcript):
            if self.fasta_set is None:
                fileobj = gzip.open(fasta_file) if fasta_file.endswith('.gz') else open(fasta_file)
                self.fasta_set = FastaInOrderAccessSet(iter(FastaIterator(fileobj)))
            if transcript is None:
                yield None
                raise StopIteration()
            chr = position.chr
            pos = position.pos
            strand = transcript.strand
            start = pos if strand == '+' else pos - 1000
            stop = pos if strand == '-' else pos + 1000
            seq = self.fasta_set.fetch(chr, start, stop)
            yield seq if strand == '+' else revcmp(seq)
        del genomic_position[:]
        del major_transcript[:]

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
