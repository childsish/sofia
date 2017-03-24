from lhc.binf.genomic_coordinate import GenomicPosition

from sofia.step import Step


class GetTranslationStartMinimumFreeEnergy(Step):
    """
    Get the minimum free energy around the start codon of the major transcript.
    """

    IN = ['major_transcript', 'chromosome_sequence_set']
    OUT = ['translation_start_mfe']
    PARAMS = ['offset', 'type']

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'major_transcript': input['major_transcript'][:]
        }
        del input['major_transcript'][:]
        return copy

    def __init__(self, offset=50, type='mfe'):
        """ Initialise the step

        :param offset: the range upstream and downstream to fold
        :param type: (mfe, efe)
        :return:
        """
        import RNA
        self.offset = offset
        self.fold = RNA.fold if type == 'mfe' else RNA.pf_fold

    def run(self, major_transcript, chromosome_sequence_set):
        for transcript in major_transcript:
            if transcript is None:
                yield None
            offset = 50
            start_position = GenomicPosition(transcript.chr,
                                             transcript.get_5p(),
                                             transcript.strand)
            interval = start_position.get_offset(-offset).get_interval(start_position.get_offset(50))
            seq = interval.get_sub_seq(chromosome_sequence_set)
            yield self.fold(seq)[1]


class GetTranslationStartMinimumFreeEnergy2(Step):
    """
    Get the minimum free energy around the start codon of the major transcript.
    """

    IN = ['genomic_interval', 'chromosome_sequence_set']
    OUT = ['translation_start_mfe']
    PARAMS = ['offset', 'type']

    def __init__(self, offset=50, type='mfe'):
        """ Initialise the step

        :param offset: the range upstream and downstream to fold
        :param type: (mfe, efe)
        :return:
        """
        import RNA
        self.offset = offset
        self.fold = RNA.fold if type == 'mfe' else RNA.pf_fold

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'genomic_interval': input['genomic_interval'][:]
        }
        del input['genomic_interval'][:]
        return copy

    def run(self, genomic_interval, chromosome_sequence_set):
        for interval in genomic_interval:
            if interval is None:
                yield None
            offset = 50
            start_position = GenomicPosition(interval.chr,
                                             interval.get_5p(),
                                             interval.strand)
            interval = start_position.get_offset(-offset).get_interval(start_position.get_offset(50))
            seq = interval.get_sub_seq(chromosome_sequence_set)
            yield self.fold(seq)[1]


class GetStructuralFeatures(Step):
    """
    Get the RNA secondary structural features of the given secondary structure.
    """

    IN = ['rna_secondary_structure']
    OUT = ['hairpin_loop', 'multiloop', 'internal_loop', 'bulge', 'stem', 'branch', 'bridge']

    def run(self, rna_secondary_structure):
        for structure in rna_secondary_structure:
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
            for i in range(len(structure)):
                if structure[i] == '(':
                    if c_lvl == 0:
                        bridges.append(len(dots))
                        dots = []
                    lvls[c_lvl].append('(')
                    lvls.append([])
                    c_lvl += 1
                elif structure[i] == ')':
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
                elif structure[i] == '.':
                    if c_lvl == 0:
                        dots.append(i)
                    lvls[c_lvl].append('.')
            bridges.append(len(dots))
            stems.append(c_stem)

            yield hloops, mloops, iloops, bulges, stems, branches, bridges
