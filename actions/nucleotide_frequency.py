from sofia_.action import Action

from collections import Counter
from modules.kmer import KmerCounter


class CodingNucleotideFrequency(Action):

    IN = ['coding_sequence']
    OUT = ['coding_nucleotide_frequency']

    def init(self, k=1):
        self.k = k

    def calculate(self, coding_sequence):
        return KmerCounter(coding_sequence, self.k)

    def format(self, coding_nucleotide_frequency):
        return str(coding_nucleotide_frequency)


class UTR5NucleotideFrequency(Action):

    IN = ['five_prime_utr']
    OUT = ['utr5_nucleotide_frequency']

    def init(self, k=1):
        self.k = k

    def calculate(self, five_prime_utr):
        return KmerCounter(five_prime_utr, self.k)

    def format(self, utr5_nucleotide_frequency):
        return str(utr5_nucleotide_frequency)


class UTR3NucleotideFrequency(Action):

    IN = ['three_prime_utr']
    OUT = ['utr3_nucleotide_frequency']

    def init(self, k=1):
        self.k = k

    def calculate(self, three_prime_utr):
        return KmerCounter(three_prime_utr, self.k)

    def format(self, utr3_nucleotide_frequency):
        return str(utr3_nucleotide_frequency)

