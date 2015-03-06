from sofia_.step import Step


class DummyRNAModule(object):
    def fold(self, seq):
        return None

    def pf_fold(self, seq):
        return None

try:
    import RNA
except ImportError:
    RNA = DummyRNAModule()


class GetTranslationStartMinimumFreeEnergy(Step):
    """
    Get the minimum free energy around the start codon of the major transcript.
    """

    IN = ['major_transcript', 'chromosome_sequence_set']
    OUT = ['translation_start_mfe']

    def init(self, offset=50, type='mfe'):
        """ Initialise the step

        :param offset: the range upstream and downstream to fold
        :param type: (mfe, efe)
        :return:
        """
        self.offset = offset
        self.fold = RNA.fold if type == 'mfe' else RNA.pf_fold

    def calculate(self, major_transcript, chromosome_sequence_set):
        start_codon = major_transcript.ivl.get_5p()
        upstream = start_codon.get_upstream(self.offset)
        downstream = start_codon.get_downstream(self.offset)
        start_codon_region = upstream.get_interval(downstream)
        return self.fold(start_codon_region)[1]


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
