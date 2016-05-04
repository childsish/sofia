from lhc.binf.skew import Skew

from sofia import Step


class GetCodingSkew(Step):
    """
    Get the nucleotide skews of the given coding sequence. AT skew is (|A| - |T|) / (|A| + |T|). GC skew is similar.
    """

    IN = ['coding_sequence']
    OUT = ['coding_skew']

    def calculate(self, coding_sequence):
        if coding_sequence is None:
            return None
        return Skew(coding_sequence)


class GetUTR5Skew(Step):

    IN = ['five_prime_utr']
    OUT = ['utr5_skew']

    def calculate(self, five_prime_utr):
        if five_prime_utr is None:
            return None
        return Skew(five_prime_utr)


class GetUTR3Skew(Step):

    IN = ['three_prime_utr']
    OUT = ['utr3_skew']

    def calculate(self, three_prime_utr):
        if three_prime_utr is None:
            return None
        return Skew(three_prime_utr)
