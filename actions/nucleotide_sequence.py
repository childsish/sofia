from sofia_.action import Action

from collections import Counter
from modules.kmer import KmerCounter


class CalculateKNucleotideFrequency(Action):

    IN = ['nucleotide_sequence']
    OUT = ['nucleotide_frequency']

    def init(self, k=None):
        self.k = k

    def calculate(self, coding_sequence):
        return KmerCounter(coding_sequence, self.k)

    def format(self, nucleotide_frequency):
        return str(nucleotide_frequency)
