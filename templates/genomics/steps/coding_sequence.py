from collections import defaultdict
from functools import reduce
from itertools import izip
from operator import add, mul

from lhc.binf.kmer import KmerCounter

from sofia.step import Step


class TranslateCodingSequence(Step):
    """
    Translates a coding sequence into an amino acid sequence using the standard genetic code.
    """

    IN = ['coding_sequence', 'genetic_code']
    OUT = ['protein_sequence']

    def calculate(self, coding_sequence, genetic_code):
        if coding_sequence is None:
            return None
        return genetic_code.translate(coding_sequence)


class GetCodonUsage(Step):
    """
    Calculate the codon usage of a coding sequence.
    """

    IN = ['coding_sequence']
    OUT = ['codon_usage']

    def calculate(self, coding_sequence):
        if coding_sequence is None:
            return None
        return KmerCounter(coding_sequence, k=3, step=3)


class GetRelativeSynonymousCodonUsage(Step):
    """
    Calculates and return the relative synonymous codon usage (rscu) and relative codon adaptiveness (w)
    as defined by Sharp et. al. 1987
    """

    IN = ['codon_usage', 'genetic_code']
    OUT = ['relative_synonymous_codon_usage', 'relative_codon_adaptiveness']

    def calculate(self, codon_usage, genetic_code):
        if codon_usage is None:
            return None, None
        rscu = {}
        w = {}
        for aa in genetic_code.AMINO_ACIDS:
            cdns = genetic_code.get_codons(aa)
            usgs = [codon_usage[cdn] for cdn in cdns]
            ttl_usg = sum(usgs) / float(len(usgs))
            if ttl_usg == 0:
                rscus = len(usgs) * [0]
                ws = len(usgs) * [0]
            else:
                rscus = [usg / ttl_usg for usg in usgs]
                ws = [usg / float(max(usgs)) for usg in usgs]
            for cdn, rscu_, w_ in izip(cdns, rscus, ws):
                rscu[cdn] = rscu_
                w[cdn] = w_
        return rscu, w


class GetCodonAdaptationIndex(Step):
    """
    Calculate the Codon Adaptation Index as defined by Sharp et. al. 1987.
    """

    IN = ['coding_sequence', 'relative_codon_adaptiveness']
    OUT = ['codon_adaptation_index']

    def calculate(self, coding_sequence, relative_codon_adaptiveness):
        if coding_sequence is None or len(coding_sequence) == 0:
            return None
        cai = []
        for i in xrange(0, len(coding_sequence), 3):
            cdn = coding_sequence[i:i+3].lower()
            #red = set(cdn) & RedundantCode.REDUNDANT_BASES
            #if len(red) > 0:
            #    warnings.warn('Redundant bases "%s" encountered in codon. Codon "%s" has been ignored.'%(','.join(sorted(red)), cdn))
            #    continue
            if cdn not in ['atg', 'tgg', 'taa', 'tga', 'tag'] and cdn in relative_codon_adaptiveness:
                cai.append(relative_codon_adaptiveness[cdn])
        return geometric_mean(cai)


class GetEffectiveNumberOfCodons(Step):
    """
    Calculated the number of effective codons (Nc) as defined by Sun et. al. 2013
    """

    IN = ['codon_usage', 'genetic_code']
    OUT = ['effective_number_of_codons']

    def calculate(self, codon_usage, genetic_code):
        if codon_usage is None:
            return None
        fs = {aa: self.calculate_f(codon_usage, genetic_code[aa])
              for aa in genetic_code.AMINO_ACIDS}
        fams = defaultdict(list)
        for aa in genetic_code.AMINO_ACIDS:
            if fs[aa] is not None:  # Assume missing aa have the mean F
                fams[len(genetic_code[aa])].append(fs[aa])
        nc = sum(len(fam_Fs) if sz == 1 else len(fam_Fs) / arithmetic_mean(fam_Fs)
                 for sz, fam_Fs in fams.iteritems())
        return nc

    def calculate_f(self, cut, fam):
        n = float(sum(cut[cdn] for cdn in fam))
        return None if n <= 1 else n * sum((cut[cdn] / n) ** 2 for cdn in fam) / (n - 1)


def arithmetic_mean(iterable):
    return reduce(add, iterable) / float(len(iterable))


def geometric_mean(iterable):
    return reduce(mul, iterable) ** (1 / float(len(iterable)))
