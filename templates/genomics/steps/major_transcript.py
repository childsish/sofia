from sofia.step import Step


class GetCodonSequenceLength(Step):

    IN = ['major_transcript']
    OUT = ['major_transcript_length']

    def run(self, major_transcript):
        for transcript in major_transcript:
            yield None if transcript is None else len(transcript)


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

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'major_transcript': input['major_transcript'][:]
        }
        del input['major_transcript'][:]
        return copy

    def run(self, chromosome_sequence_set, major_transcript):
        for transcript in major_transcript:
            if transcript is None:
                yield None
                continue

            buffer_key = (id(chromosome_sequence_set), id(transcript))
            if buffer_key in self.buffer:
                yield self.buffer[buffer_key]
                continue

            res = transcript.get_sub_seq(chromosome_sequence_set, types={'CDS'})
            if len(res) % 3 != 0:
                self.invalid.append(str(transcript))

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
