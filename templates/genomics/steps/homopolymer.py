from sofia.step import Step, EndOfStream


class GetHomopolymer(Step):
    """
    Get the stretch of identical nucleotides at the variant
    """
    
    IN = ['genomic_position', 'chromosome_sequence_segment']
    OUT = ['homopolymer']

    def __init__(self):
        self.position = None
        self.segments = []

    def run(self, ins, outs):
        position = self.position
        segments = self.segments

        while len(ins.genomic_position) > 0 and len(ins.chromosome_sequence_segment) > 0:
            if position is None:
                position = ins.genomic_position.pop()
            if position is EndOfStream:
                outs.homopolymer.push(EndOfStream)
                return True

            i = 0
            while i < len(segments) and segments[i].stop < position:
                i += 1
            del segments[:i]

            while position is not None and len(ins.chromosome_sequence_segment) > 0:
                segment = ins.chromosome_sequence_segment.peek()
                if segment is EndOfStream:
                    outs.homopolymer.push(self.get_homopolymer(position, segments), EndOfStream)
                    return True

                if segment.start > position:
                    if not outs.homopolymer.push(self.get_homopolymer(position, segments)):
                        self.position = None
                        return False
                    position = None
                elif segment.stop > position:
                    segments.append(ins.chromosome_sequence_segment.pop())
        self.position = position

    def get_homopolymer(self, position, segments):
        return ''.join(segments)[position - segments[0].start:position - segments[-1].stop]
