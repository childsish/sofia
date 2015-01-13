from sofia_.action import Action


class GetUpstreamSequence(Action):
    """
    Get the region 1000 nucleotides upstream of the major transcript transcriptional start site.
    """

    IN = ['major_transcript', 'chromosome_sequence_set']
    OUT = ['upstream_sequence']

    def init(self, offset=1000):
        self.offset = offset

    def calculate(self, major_transcript, chromosome_sequence_set):
        start_pos = major_transcript.ivl.get_5p()
        upstream_pos = start_pos.get_upstream(self.offset)
        return start_pos.get_interval(upstream_pos)


class GetUpstreamORFs(Action):
    """
    Get the ORFs in the upstream region.
    """

    IN = ['upstream_sequence', 'genetic_code']
    OUT = ['upstream_orfs']

    def calculate(self, upstream_sequence, genetic_code):
        stops = genetic_code.translate('*')
        res = []
        for i in xrange(len(upstream_sequence)):
            if not upstream_sequence[i:i + 3] == 'atg':
                continue
            for j in xrange(i, len(upstream_sequence), 3):
                if upstream_sequence[j:j + 3] in stops:
                    res.append(upstream_sequence[i:j + 3])
        return res


class GetNumberOfUpstreamORFs(Action):

    IN = ['upstream_orfs']
    OUT = ['number_of_upstream_orfs']

    def calculate(self, upstream_orfs):
        return len(upstream_orfs)
