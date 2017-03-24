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

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'major_transcript': input['major_transcript'][:]
        }
        del input['major_transcript'][:]
        return copy

    def run(self, major_transcript, chromosome_sequence_set):
        for transcript in major_transcript:
            ivl = transcript.ivl
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

    def consume_input(self, input):
        copy = {
            'chromosome_sequence_set': input['chromosome_sequence_set'][0],
            'genomic_interval': input['genomic_interval'][:]
        }
        del input['genomic_interval'][:]
        return copy

    def run(self, genomic_interval, chromosome_sequence_set):
        for interval in genomic_interval:
            start_pos = GenomicPosition(interval.chr, interval.get_5p(), interval.strand)
            upstream_pos = start_pos.get_offset(-self.offset)
            yield start_pos.get_interval(upstream_pos).get_sub_seq(chromosome_sequence_set)


class GetUpstreamORFs(Step):
    """
    Get the ORFs in the upstream region.
    """

    IN = ['upstream_sequence', 'genetic_code']
    OUT = ['upstream_orfs']

    def consume_input(self, input):
        copy = {
            'genetic_code': input['genetic_code'][0],
            'upstream_sequence': input['upstream_sequence'][:]
        }
        del input['upstream_sequence'][:]
        return copy

    def run(self, upstream_sequence, genetic_code):
        for sequence in upstream_sequence:
            stops = genetic_code.get_codons('*')
            res = []
            for i in range(len(sequence)):
                if not sequence[i:i + 3] == 'atg':
                    continue
                for j in range(i, len(sequence), 3):
                    if sequence[j:j + 3] in stops:
                        res.append(sequence[i:j + 3])
            yield res


class GetNumberOfUpstreamORFs(Step):

    IN = ['upstream_orfs']
    OUT = ['number_of_upstream_orfs']

    def run(self, upstream_orfs):
        for orf in upstream_orfs:
            yield len(orf)
