from lhc.binf.kmer import KmerCounter

from sofia.step import Step


class GetCodingKmer(Step):

    IN = ['coding_sequence']
    OUT = ['coding_kmer']

    def run(self, coding_sequence):
        for sequence in coding_sequence:
            yield None if sequence is None else KmerCounter(sequence)


class GetUTR5Kmer(Step):

    IN = ['five_prime_utr']
    OUT = ['utr5_kmer']

    def run(self, five_prime_utr):
        for utr in five_prime_utr:
            yield None if utr is None else KmerCounter(utr)


class GetUTR3Kmer(Step):

    IN = ['three_prime_utr']
    OUT = ['utr3_kmer']

    def run(self, three_prime_utr):
        for utr in three_prime_utr:
            yield None if utr is None else KmerCounter(utr)


class GetProteinKmer(Step):

    IN = ['protein_sequence']
    OUT = ['protein_kmer']

    def run(self, protein_sequence):
        for sequence in protein_sequence:
            yield None if sequence is None else KmerCounter(sequence)
