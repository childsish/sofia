from sofia_.action import Action

from collections import Counter


class GetCodingNucleotideSkew(Action):
    """
    Get the nucleotide skews of the given coding sequence. AT skew is (|A| - |T|) / (|A| + |T|). GC skew is similar.
    """

    IN = ['coding_sequence']
    OUT = ['coding_nucleotide_skew']

    def init(self, skew='at'):
        self.skew = skew.lower()

    def calculate(self, coding_sequence):
        return get_skew(coding_sequence, self.skew)


class GetUTR5NucleotideSkew(Action):

    IN = ['five_prime_utr']
    OUT = ['utr5_nucleotide_skew']

    def init(self, skew='at'):
        self.skew = skew.lower()

    def calculate(self, five_prime_utr):
        return get_skew(five_prime_utr, self.skew)


class GetUTR3NucleotideSkew(Action):

    IN = ['three_prime_utr']
    OUT = ['utr3_nucleotide_skew']

    def init(self, skew='at'):
        self.skew = skew.lower()

    def calculate(self, three_prime_utr):
        return get_skew(three_prime_utr, self.skew)


def get_skew(seq, skew):
    cnt = Counter(seq.lower())
    at = cnt['a'] - cnt['t'] / float(cnt['a'] + cnt['t'])
    gc = cnt['g'] - cnt['c'] / float(cnt['g'] + cnt['c'])
    if skew == 'at':
        return at
    elif skew == 'gc':
        return gc
    return {'at': at, 'gc': gc}
