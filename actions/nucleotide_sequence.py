from sofia_.action import Action
from modules.kmer import KmerCounter


class GetKNucleotideFrequency(Action):

    IN = ['nucleotide_sequence']
    OUT = ['nucleotide_frequency']

    def init(self, k=None):
        self.k = k

    def calculate(self, coding_sequence):
        return KmerCounter(coding_sequence, self.k)

    def format(self, nucleotide_frequency):
        return str(nucleotide_frequency)
