from sofia.step import Step


class GetCodonSequenceLength(Step):

    IN = ['major_transcript']
    OUT = ['major_transcript_length']

    def run(self, major_transcript):
        if major_transcript is None:
            return None
        return len(major_transcript)


class GetMajorTranscriptCodingSequence(Step):
    """
    Get the coding sequence of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def init(self):
        self.buffer = {}
        self.max_buffer = 10
        self.invalid = []

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None

        buffer_key = (id(chromosome_sequence_set), id(major_transcript))
        if buffer_key in self.buffer:
            return self.buffer[buffer_key]

        res = major_transcript.get_sub_seq(chromosome_sequence_set, types={'CDS'})
        if len(res) % 3 != 0:
            self.invalid.append(str(major_transcript))

        if len(self.buffer) > self.max_buffer:
            self.buffer.popitem()
        self.buffer[buffer_key] = res
        return res

    def get_user_warnings(self):
        return ['{} coding sequence length not a multiple of 3, possible mis-annotation'.format(invalid)
                for invalid in self.invalid]


class GetFivePrimeUtr(Step):
    """
    Get the 5' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['five_prime_utr']

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.get_sub_seq(chromosome_sequence_set, type="5'UTR5")


class GetThreePrimeUtr(Step):
    """
    Get the 3' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['three_prime_utr']

    def run(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.get_sub_seq(chromosome_sequence_set, type="3'UTR")
