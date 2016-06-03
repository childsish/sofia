from sofia.step import Step


class GetCodonSequenceLength(Step):

    IN = ['major_transcript']
    OUT = ['major_transcript_length']

    def run(self, major_transcript):
        if major_transcript is None:
            yield None
        yield len(major_transcript)


class GetMajorTranscriptCodingSequence(Step):
    """
    Get the coding sequence of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def __init__(self):
        self.buffer = {}
        self.max_buffer = 10
        self.invalid = []

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            yield None
            raise StopIteration()

        buffer_key = (id(chromosome_sequence_set), id(major_transcript))
        if buffer_key in self.buffer:
            yield self.buffer[buffer_key]
            raise StopIteration()

        res = major_transcript.get_sub_seq(chromosome_sequence_set, types={'CDS'})
        if len(res) % 3 != 0:
            self.invalid.append(str(major_transcript))

        if len(self.buffer) > self.max_buffer:
            self.buffer.popitem()
        self.buffer[buffer_key] = res
        yield res

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

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            yield None
        yield major_transcript.get_sub_seq(chromosome_sequence_set, type="5'UTR5")


class GetThreePrimeUtr(Step):
    """
    Get the 3' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['three_prime_utr']

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            yield None
        yield major_transcript.get_sub_seq(chromosome_sequence_set, type="3'UTR")
