from collections import defaultdict
from operator import add, mul

from lhc.binf.kmer import KmerCounter

from sofia.step import Step


class TranslateCodingSequence(Step):
    """
    Translates a coding sequence into an amino acid sequence using the standard genetic code.
    """

    IN = ['coding_sequence', 'genetic_code']
    OUT = ['protein_sequence']

    def consume_input(self, input):
        copy = {
            'coding_sequence': input['coding_sequence'][:],
            'genetic_code': input['genetic_code'][0]
        }
        del input['coding_sequence'][:]
        return copy

    def run(self, coding_sequence, genetic_code):
        for sequence in coding_sequence:
            if sequence is None:
                yield None
            yield genetic_code.translate(sequence)


class GetCodonUsage(Step):
    """
    Calculate the codon usage of a coding sequence.
    """

    IN = ['coding_sequence']
    OUT = ['codon_usage']

    def run(self, coding_sequence):
        for sequence in coding_sequence:
            if sequence is None:
                yield None
            yield KmerCounter(sequence, k=3, step=3)


class GetRelativeSynonymousCodonUsage(Step):
    """
    Calculates and return the relative synonymous codon usage (rscu) and relative codon adaptiveness (w)
    as defined by Sharp et. al. 1987
    """

    IN = ['codon_usage', 'genetic_code']
    OUT = ['relative_synonymous_codon_usage', 'relative_codon_adaptiveness']

    def consume_input(self, input):
        copy = {
            'codon_usage': input['codon_usage'][:],
            'genetic_code': input['genetic_code'][0]
        }
        del input['codon_usage'][:]
        return copy

    def run(self, codon_usage, genetic_code):
        for usage in codon_usage:
            if usage is None:
                yield None, None
            rscu = {}
            w = {}
            for aa in genetic_code.AMINO_ACIDS:
                cdns = genetic_code.get_codons(aa)
                usgs = [usage[cdn] for cdn in cdns]
                ttl_usg = sum(usgs) / float(len(usgs))
                if ttl_usg == 0:
                    rscus = len(usgs) * [0]
                    ws = len(usgs) * [0]
                else:
                    rscus = [usg / ttl_usg for usg in usgs]
                    ws = [usg / float(max(usgs)) for usg in usgs]
                for cdn, rscu_, w_ in zip(cdns, rscus, ws):
                    rscu[cdn] = rscu_
                    w[cdn] = w_
            yield rscu, w


class GetCodonAdaptationIndex(Step):
    """
    Calculate the Codon Adaptation Index as defined by Sharp et. al. 1987.
    """

    IN = ['coding_sequence', 'relative_codon_adaptiveness']
    OUT = ['codon_adaptation_index']

    def run(self, coding_sequence, relative_codon_adaptiveness):
        for sequence, adaptiveness in zip(coding_sequence, relative_codon_adaptiveness):
            if sequence is None or len(sequence) == 0:
                yield None
            cai = []
            for i in range(0, len(sequence), 3):
                cdn = sequence[i:i+3].lower()
                #red = set(cdn) & RedundantCode.REDUNDANT_BASES
                #if len(red) > 0:
                #    warnings.warn('Redundant bases "%s" encountered in codon. Codon "%s" has been ignored.'%(','.join(sorted(red)), cdn))
                #    continue
                if cdn not in ['atg', 'tgg', 'taa', 'tga', 'tag'] and cdn in adaptiveness:
                    cai.append(adaptiveness[cdn])
            yield geometric_mean(cai)


class GetEffectiveNumberOfCodons(Step):
    """
    Calculated the number of effective codons (Nc) as defined by Sun et. al. 2013
    """

    IN = ['codon_usage', 'genetic_code']
    OUT = ['effective_number_of_codons']

    def consume_input(self, input):
        copy = {
            'codon_usage': input['codon_usage'][:],
            'genetic_code': input['genetic_code'][0]
        }
        del input['codon_usage'][:]
        return copy

    def run(self, codon_usage, genetic_code):
        for usage in codon_usage:
            if usage is None:
                yield None
            fs = {aa: self.run_f(usage, genetic_code[aa])
                  for aa in genetic_code.AMINO_ACIDS}
            fams = defaultdict(list)
            for aa in genetic_code.AMINO_ACIDS:
                if fs[aa] is not None:  # Assume missing aa have the mean F
                    fams[len(genetic_code[aa])].append(fs[aa])
            nc = sum(len(fam_Fs) if sz == 1 else len(fam_Fs) / arithmetic_mean(fam_Fs)
                     for sz, fam_Fs in fams.items())
            yield nc

    def run_f(self, cut, fam):
        n = float(sum(cut[cdn] for cdn in fam))
        return None if n <= 1 else n * sum((cut[cdn] / n) ** 2 for cdn in fam) / (n - 1)


def arithmetic_mean(iterable):
    sum = 0
    total = 0.
    for item in iterable:
        sum += item
        total += 1
    return sum / total


def geometric_mean(iterable):
    product = 1
    total = 0.
    for item in iterable:
        product *= item
        total += 1
    return product ** (1 / total)
