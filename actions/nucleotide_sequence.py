from sofia_.action import Action
from lhc.binf.kmer import KmerCounter


class GetKNucleotideFrequency(Action):
    """
    Tally the number of times A, C, G and T are used in the given sequence.
    """

    IN = ['nucleotide_sequence']
    OUT = ['nucleotide_frequency']

    def init(self, k=None):
        self.k = k

    def calculate(self, coding_sequence):
        return KmerCounter(coding_sequence, self.k)

    def format(self, nucleotide_frequency):
        return str(nucleotide_frequency)
