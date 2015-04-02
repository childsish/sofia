from lhc.binf.genomic_coordinate import Position
from sofia_.step import Step
from warnings import warn


class DummyRNAModule(object):
    def fold(self, seq):
        return None

    def pf_fold(self, seq):
        return None


class GetTranslationStartMinimumFreeEnergy(Step):
    """
    Get the minimum free energy around the start codon of the major transcript.
    """

    IN = ['major_transcript', 'chromosome_sequence_set']
    OUT = ['translation_start_mfe']

    def init(self):
        try:
            import RNA
            self.fold = RNA.fold
        except ImportError:
            warn('RNAfold library not installed.')
            self.fold = lambda seq: (None, None)

    def calculate(self, major_transcript, chromosome_sequence_set):
        offset = 50
        start_position = Position(major_transcript.chr,
                                  major_transcript.get_5p(),
                                  major_transcript.strand)
        interval = start_position.get_offset(-offset).get_interval(start_position.get_offset(50))
        seq = interval.get_sub_seq(chromosome_sequence_set)
        return self.fold(seq)[1]


class GetStructuralFeatures(Step):
    """
    Incomplete. Get the RNA secondary structural features of the given sequence.
    """

    IN = ['rna_secondary_structure']
    OUT = ['rna_secondary_structure_features']


def structural_features(stc):
    hloops = []
    mloops = []
    iloops = []
    bulges = []
    stems = []
    branches = []
    bridges = []
    
    lvls = [[]]
    dots = []
    c_lvl = 0
    c_stem = 0
    for i in xrange(len(stc)):
        if stc[i] == '(':
            if c_lvl == 0:
                bridges.append(len(dots))
                dots = []
            lvls[c_lvl].append('(')
            lvls.append([])
            c_lvl += 1
        elif stc[i] == ')':
            p_lvl = lvls.pop()
            c_lvl -= 1
            
            if p_lvl.count('(') == 0:
                hloops.append(len(p_lvl))
            elif p_lvl.count('(') == 1 and p_lvl.count('.') > 0:
                if p_lvl[0] == '.' and p_lvl[-1] == '.':
                    iloops.append((p_lvl.index('('), len(p_lvl) - p_lvl.index('(') - 1))
                else:
                    bulges.append(len(p_lvl)-1)
            elif '.' in p_lvl:
                mloops.append(len(p_lvl) - p_lvl.count('('))
                branches.append(p_lvl.count('('))
            
            if p_lvl != ['('] and c_stem != 0:
                stems.append(c_stem)
                c_stem = 0
            c_stem += 1
        elif stc[i] == '.':
            if c_lvl == 0:
                dots.append(i)
            lvls[c_lvl].append('.')
    bridges.append(len(dots))
    stems.append(c_stem)

    return hloops, mloops, iloops, bulges, stems, branches, bridges
