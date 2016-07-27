from sofia.step import Step, EndOfStream


class GetCodonSequenceLength(Step):

    IN = ['major_transcript']
    OUT = ['major_transcript_length']

    def run(self, ins, outs):
        while len(ins) > 0:
            transcript = ins.major_transcript.pop()
            if transcript is EndOfStream:
                outs.major_transcript_length.push(EndOfStream)
                return True
            length = None if transcript is None else len(transcript)
            if not outs.major_transcript_length.push(length):
                break
        return len(ins) == 0


class GetMajorTranscriptCodingSequence(Step):
    """
    Get the coding sequence of the major transcript.
    """

    IN = ['major_transcript', 'chromosome_sequence_segment']
    OUT = ['coding_sequence']

    def __init__(self):
        self.transcript = None
        self.segments = []

    def run(self, ins, outs):
        transcript = self.transcript
        segments = self.segments

        while len(ins.major_transcript) > 0 and len(ins.chromosome_sequence_segment) > 0:
            if transcript is None:
                transcript = ins.major_transcript.pop()
            if transcript is EndOfStream:
                outs.coding_sequence.push(EndOfStream)
                return True

            i = 0
            while i < len(segments) and segments[i].stop < transcript.start:
                i += 1
            del segments[:i]

            while transcript is not None and len(ins.chromosome_sequence_segment) > 0:
                segment = ins.chromosome_sequence_segment.peek()
                if segment is EndOfStream:
                    outs.homopolymer.push(self.get_coding_sequence(transcript, segments), EndOfStream)
                    return True

                if segment.start >= transcript.stop:
                    if not outs.homopolymer.push(self.get_coding_sequence(transcript, segments)):
                        self.transcript = None
                        return False
                    transcript = None
                elif segment.stop >= transcript.start:
                    segments.append(ins.chromosome_sequence_segment.pop())
        self.transcript = transcript

    def get_coding_sequence(self, position, segments):
        return ''.join(segments)[position - segments[0].start:position - segments[-1].stop]

    def get_user_warnings(self):
        return ['{} coding sequence length not a multiple of 3, possible mis-annotation'.format(invalid)
                for invalid in self.invalid]

    @classmethod
    def get_out_resolvers(cls):
        return {
            'sync': cls.resolve_out_sync
        }

    @classmethod
    def resolve_out_sync(cls, ins):
        return {
            'coding_sequence': ins['major_transcript']
        }


class GetFivePrimeUtr(Step):
    """
    Get the 5' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['five_prime_utr']

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'major_transcript': input['major_transcript'][:]
        }
        del input['major_transcript'][:]
        return copy

    def run(self, chromosome_sequence_set, major_transcript):
        chromosome_sequence_set = chromosome_sequence_set[0]
        for transcript in major_transcript:
            yield None if transcript is None else transcript.get_sub_seq(chromosome_sequence_set, type="5'UTR5")
        del major_transcript[:]


class GetThreePrimeUtr(Step):
    """
    Get the 3' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['three_prime_utr']

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'major_transcript': input['major_transcript'][:]
        }
        del input['major_transcript'][:]
        return copy

    def run(self, chromosome_sequence_set, major_transcript):
        chromosome_sequence_set = chromosome_sequence_set[0]
        for transcript in major_transcript:
            yield None if transcript is None else transcript.get_sub_seq(chromosome_sequence_set, type="3'UTR")
        del major_transcript[:]
