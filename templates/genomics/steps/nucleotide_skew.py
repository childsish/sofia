from lhc.binf.skew import Skew

from sofia.step import Step


class GetCodingSkew(Step):
    """
    Get the nucleotide skews of the given coding sequence. AT skew is (|A| - |T|) / (|A| + |T|). GC skew is similar.
    """

    IN = ['coding_sequence']
    OUT = ['coding_skew']

    def run(self, coding_sequence):
        for sequence in coding_sequence:
            yield None if sequence is None else Skew(sequence)


class GetUTR5Skew(Step):

    IN = ['five_prime_utr']
    OUT = ['utr5_skew']

    def run(self, five_prime_utr):
        for utr in five_prime_utr:
            yield None if utr is None else Skew(utr)


class GetUTR3Skew(Step):

    IN = ['three_prime_utr']
    OUT = ['utr3_skew']

    def run(self, three_prime_utr):
        for utr in three_prime_utr:
            yield None if utr is None else Skew(utr)
