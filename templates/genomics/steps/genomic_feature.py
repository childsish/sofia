from sofia.step import Step


class GetMajorTranscriptFromGenomicFeature(Step):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_feature']
    OUT = ['major_transcript']

    def run(self, genomic_feature):
        if genomic_feature is None or len(genomic_feature.children) == 0:
            yield None
        transcripts = sorted(genomic_feature.children, key=self.get_transcript_length)
        yield transcripts[-1]

    @staticmethod
    def get_transcript_length(transcript):
        return sum(len(child) for child in transcript.children if child.type == 'CDS')


#class GetMajorTranscriptFromGenomicInterval(Step):
#    """
#    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
#    """

#    IN = ['genomic_interval']
#    OUT = ['major_transcript']

#    def run(self, genomic_interval):
#        return genomic_interval
