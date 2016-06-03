from lhc.binf.kmer import KmerCounter

from sofia.step import Step


class GetCodingKmer(Step):

    IN = ['coding_sequence']
    OUT = ['coding_kmer']

    def run(self, coding_sequence):
        if coding_sequence is None:
            yield None
        yield KmerCounter(coding_sequence)


class GetUTR5Kmer(Step):

    IN = ['five_prime_utr']
    OUT = ['utr5_kmer']

    def run(self, five_prime_utr):
        if five_prime_utr is None:
            yield None
        yield KmerCounter(five_prime_utr)


class GetUTR3Kmer(Step):

    IN = ['three_prime_utr']
    OUT = ['utr3_kmer']

    def run(self, three_prime_utr):
        if three_prime_utr is None:
            yield None
        yield KmerCounter(three_prime_utr)


class GetProteinKmer(Step):

    IN = ['protein_sequence']
    OUT = ['protein_kmer']

    def run(self, protein_sequence):
        if protein_sequence is None:
            yield None
        yield KmerCounter(protein_sequence)
