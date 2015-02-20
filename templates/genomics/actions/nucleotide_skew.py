from sofia_.action import Action

from collections import Counter
from lhc.binf.skew import Skew


class GetCodingSkew(Action):
    """
    Get the nucleotide skews of the given coding sequence. AT skew is (|A| - |T|) / (|A| + |T|). GC skew is similar.
    """

    IN = ['coding_sequence']
    OUT = ['coding_skew']

    def calculate(self, coding_sequence):
        if coding_sequence is None:
            return None
        return Skew(coding_sequence)


class GetUTR5Skew(Action):

    IN = ['five_prime_utr']
    OUT = ['utr5_skew']

    def calculate(self, five_prime_utr):
        if five_prime_utr is None:
            return None
        return Skew(five_prime_utr)


class GetUTR3Skew(Action):

    IN = ['three_prime_utr']
    OUT = ['utr3_skew']

    def calculate(self, three_prime_utr):
        if three_prime_utr is None:
            return None
        return Skew(three_prime_utr)
