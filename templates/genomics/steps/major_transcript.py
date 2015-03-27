from sofia_.step import Step
from warnings import warn


class GetMajorTranscriptCodingSequence(Step):
    """
    Get the coding sequence of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def init(self):
        self.buffer = {}
        self.max_buffer = 10

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None

        buffer_key = (chromosome_sequence_set.fname, major_transcript.name)
        if buffer_key in self.buffer:
            return self.buffer[buffer_key]

        res = major_transcript.get_sub_seq(chromosome_sequence_set, types={'CDS'})
        if len(res) % 3 != 0:
            warn('{} coding sequence length not a multiple of 3, possible mis-annotation'.format(major_transcript.name))
            #return None

        if len(self.buffer) > self.max_buffer:
            self.buffer.popitem()
        self.buffer[buffer_key] = res
        return res


class GetFivePrimeUtr(Step):
    """
    Get the 5' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['five_prime_utr']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.get_sub_seq(chromosome_sequence_set, type="5'UTR5")


class GetThreePrimeUtr(Step):
    """
    Get the 3' untranslated region of the major transcript.
    """

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['three_prime_utr']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.get_sub_seq(chromosome_sequence_set, type="3'UTR")
