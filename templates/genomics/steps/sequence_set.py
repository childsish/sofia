from lhc.binf.sequence import revcmp

from sofia.step import Step


class GetDownstream1000(Step):
    """
    Get the sequence from the given genomic position to 1000 nucleotides downstream.
    """

    IN = ['chromosome_sequence_set', 'genomic_position', 'major_transcript']
    OUT = ['downstream_1000']
    
    def run(self, chromosome_sequence_set, genomic_position, major_transcript):
        if major_transcript is None:
            yield None
            raise StopIteration()
        chr = genomic_position.chr
        pos = genomic_position.pos
        strand = major_transcript.strand
        start = pos if strand == '+' else pos - 1000
        stop = pos if strand == '-' else pos + 1000
        seq = chromosome_sequence_set.fetch(chr, start, stop)
        yield seq if strand == '+' else revcmp(seq)

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
