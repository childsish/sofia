from lhc.binf.genomic_coordinate import GenomicPosition

from sofia.step import Step


class GetUpstreamSequence(Step):
    """
    Get the region 1000 nucleotides upstream of the major transcript transcriptional start site.
    """

    IN = ['major_transcript', 'chromosome_sequence_set']
    OUT = ['upstream_sequence']
    PARAMS = ['offset']

    def __init__(self, offset=1000):
        self.offset = offset

    def run(self, major_transcript, chromosome_sequence_set):
        ivl = major_transcript.ivl
        start_pos = GenomicPosition(ivl.chr, ivl.get_5p(), ivl.strand)
        upstream_pos = start_pos.get_offset(-self.offset)
        yield start_pos.get_interval(upstream_pos).get_sub_seq(chromosome_sequence_set)


class GetUpstreamSequence2(Step):
    """
    Get the region 1000 nucleotides upstream of the major transcript transcriptional start site.
    """

    IN = ['genomic_interval', 'chromosome_sequence_set']
    OUT = ['upstream_sequence']
    PARAMS = ['offset']

    def __init__(self, offset=1000):
        self.offset = offset

    def run(self, genomic_interval, chromosome_sequence_set):
        ivl = genomic_interval
        start_pos = GenomicPosition(ivl.chr, ivl.get_5p(), ivl.strand)
        upstream_pos = start_pos.get_offset(-self.offset)
        yield start_pos.get_interval(upstream_pos).get_sub_seq(chromosome_sequence_set)


class GetUpstreamORFs(Step):
    """
    Get the ORFs in the upstream region.
    """

    IN = ['upstream_sequence', 'genetic_code']
    OUT = ['upstream_orfs']

    def run(self, upstream_sequence, genetic_code):
        stops = genetic_code.get_codons('*')
        res = []
        for i in xrange(len(upstream_sequence)):
            if not upstream_sequence[i:i + 3] == 'atg':
                continue
            for j in xrange(i, len(upstream_sequence), 3):
                if upstream_sequence[j:j + 3] in stops:
                    res.append(upstream_sequence[i:j + 3])
        yield res


class GetNumberOfUpstreamORFs(Step):

    IN = ['upstream_orfs']
    OUT = ['number_of_upstream_orfs']

    def run(self, upstream_orfs):
        yield len(upstream_orfs)
