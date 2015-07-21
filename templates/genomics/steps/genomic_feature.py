from sofia_.step import Step


class GetMajorTranscriptFromGenomicFeature(Step):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_feature']
    OUT = ['major_transcript']

    def calculate(self, genomic_feature):
        if genomic_feature is None or len(genomic_feature.children) == 0:
            return None
        transcripts = sorted(genomic_feature.children, key=self.get_transcript_length)
        return transcripts[-1]

    @staticmethod
    def get_transcript_length(transcript):
        return sum(len(child) for child in transcript.children if child.type == 'CDS')


class GetCodingSequenceFromGenomicInterval(Step):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_interval', 'chromosome_sequence_set']
    OUT = ['coding_sequence']

    def calculate(self, genomic_interval, chromosome_sequence_set):
        return genomic_interval.get_sub_seq(chromosome_sequence_set)
