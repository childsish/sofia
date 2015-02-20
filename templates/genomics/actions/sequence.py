from sofia_.action import Action
from lhc.binf.kmer import KmerCounter


class GetCodingKmer(Action):

    IN = ['coding_sequence']
    OUT = ['coding_kmer']

    def calculate(self, coding_sequence):
        if coding_sequence is None:
            return None
        return KmerCounter(coding_sequence)


class GetUTR5Kmer(Action):

    IN = ['five_prime_utr']
    OUT = ['utr5_kmer']

    def calculate(self, five_prime_utr):
        if five_prime_utr is None:
            return None
        return KmerCounter(five_prime_utr)


class GetUTR3Kmer(Action):

    IN = ['three_prime_utr']
    OUT = ['utr3_kmer']

    def calculate(self, three_prime_utr):
        if three_prime_utr is None:
            return None
        return KmerCounter(three_prime_utr)


class GetProteinKmer(Action):

    IN = ['protein_sequence']
    OUT = ['protein_kmer']

    def calculate(self, protein_sequence):
        if protein_sequence is None:
            return None
        return KmerCounter(protein_sequence)
