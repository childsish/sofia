from sofia_.features import Feature

from lhc.binf.sequence import revcmp

class GetCodingSequenceByGeneModel(Feature):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set)#, type='CDS')

class GetDownstream1000(Feature):

    IN = ['chromosome_sequence_set', 'genomic_position', 'major_transcript']
    OUT = ['downstream_1000']
    
    def calculate(self, chromosome_sequence_set, genomic_position, major_transcript):
        if major_transcript is None:
            return None
        chr = genomic_position['chromosome_id']
        pos = genomic_position['chromosome_pos']
        strand = major_transcript.ivl.strand
        start = pos if strand == '+' else pos - 1000
        stop = pos if strand == '-' else pos + 1000
        seq = chromosome_sequence_set.getInterval(chr, start, stop)
        return seq if strand == '+' else revcmp(seq)
