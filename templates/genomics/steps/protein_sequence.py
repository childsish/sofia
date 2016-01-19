from sofia_.step import Step

from collections import Counter
from itertools import islice, izip
from warnings import warn


class GetPest(Step):
    """
    Finds regions rich in P, E, S and T. These sequences are associated with protein that have a short half life.
    PEST rich is defined by Rogers et. al. (1986).
    """

    IN = ['protein_sequence', 'molecular_weight_set']
    OUT = ['pest_sequences']
    PARAMETERS = ['win', 'thr', 'mono']

    POSITIVE = set('RHK')
    REQUIRED = ('P', 'DE', 'ST')
    
    def init(self, win=12, thr=5, mono=False):
        self.win = win
        self.thr = thr
        self.mono = 'mono' if mono else 'avg'

    def calculate(self, protein_sequence, molecular_weight_set):
        if protein_sequence is None:
            return None
        protein_sequence = protein_sequence.rstrip('*')
        if '*' in protein_sequence:
            warn('protein sequence terminates early')
            return None
        return list(self.iter_pest(protein_sequence, molecular_weight_set))

    def iter_pest(self, seq, molwts):
        """ Algorithm copied from EMBOSS:
            https://github.com/pjotrp/EMBOSS/blob/master/emboss/epestfind.c:278
        """
        ltkdhi = dict(izip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                           [63, 10, 70, 10, 10, 72, 41, 13, 90, 0, 6, 82, 64, 10, 0, 29, 10,
                            0, 36, 38, 0, 87, 36, 45, 58, 10]))
        for fr, to in self.iter_candidates(seq):
            cnt = Counter(islice(seq, fr, to))  # islice to prevent copying
            if self.is_valid_pest(cnt):
                molwt = sum(molwts[seq[i]][self.mono] for i in xrange(fr, to))
                pstsum = sum(cnt[k] * molwts[k][self.mono] for k in 'DEPST')
                pstsum -= sum(molwts[k][self.mono] for k in 'EPT')
                pstpct = pstsum / molwt
                hydind = sum(v * molwts[k][self.mono] * ltkdhi[k] / molwt for k, v in cnt.iteritems())
                pstscr = 0.55 * pstpct - 0.5 * hydind
                yield pstscr, (fr, to)
    
    def iter_candidates(self, seq):
        fr = 0
        while fr < len(seq):
            while fr < len(seq) and seq[fr] in self.POSITIVE:
                fr += 1
            to = fr + 1
            while to < len(seq) and seq[to] not in self.POSITIVE:
                to += 1
            if to - fr >= self.win:
                yield fr, to
            fr = to
    
    def is_valid_pest(self, cnt):
        return all(sum(cnt[r] for r in req) for req in self.REQUIRED)


class GetNumberOfPestSequences(Step):

    IN = ['pest_sequences']
    OUT = ['number_of_pest_sequences']

    def calculate(self, pest_sequences):
        if pest_sequences is None:
            return None
        return len(pest_sequences)


class GetAveragePestSequenceLength(Step):

    IN = ['pest_sequences']
    OUT = ['average_pest_sequence_length']

    def calculate(self, pest_sequences):
        if pest_sequences is None or len(pest_sequences) == 0:
            return None
        return sum(len(seq) for seq in pest_sequences) / float(len(pest_sequences))


class GetAminoAcidFrequency(Step):

    IN = ['protein_sequence']
    OUT = ['amino_acid_frequency']

    def calculate(self, protein_sequence):
        if protein_sequence is None:
            return None
        return Counter(protein_sequence)
