import gzip

from lhc.binf.sequence import revcmp
from sofia.step import Step, EndOfStream


class GetDownstream1000(Step):
    """
    Get the sequence from the given genomic position to 1000 nucleotides downstream.
    """

    IN = ['genomic_position', 'major_transcript', 'chromosome_sequence_segment']
    OUT = ['downstream_1000']

    def __init__(self):
        self.position = None
        self.transcript = None
        self.segments = []
    
    def run(self, ins, outs):
        position = self.position
        transcript = self.transcript
        segments = self.segments

        while len(ins.genomic_position) > 0 and len(ins.major_transcript) > 0 and len(ins.chromosome_sequence_segment) > 0:
            if position is None:
                position = ins.genomic_position.pop()
                transcript = ins.major_transcript.pop()
            if position is EndOfStream or transcript is EndOfStream:
                outs.downstream_1000.push(EndOfStream)
                return True
            five_adj = -1000 if transcript.strand == '-' else 0
            three_adj = 1000 if transcript.strand == '+' else 0

            i = 0
            while i < len(segments) and segments[i].stop < position + five_adj:
                i += 1
            del segments[:i]

            while position is not None and len(ins.chromosome_sequence_segment) > 0:
                segment = ins.chromosome_sequence_segment.peek()
                if segment is EndOfStream:
                    outs.downstream_1000.push(self.get_downstream_1000(position + five_adj, position + three_adj, transcript, segments), EndOfStream)
                    return True

                if segment.start > position + three_adj:
                    if not outs.downstream_1000.push(self.get_downstream_1000(position + five_adj, position + three_adj, transcript, segments)):
                        self.position = None
                        self.transcript = None
                        return False
                elif segment.stop > position + five_adj:
                    segments.append(ins.chromosome_sequence_segment.pop())
        self.position = position
        self.transcript = transcript

    def get_downstream_1000(self, start, stop, transcript, segments):
        downstream_1000 = ''.join(segments)[start - segments[0].start:stop - segments[0].start]
        return downstream_1000 if transcript.strand == '+' else revcmp(downstream_1000)

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
