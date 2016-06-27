from sofia.step import Step


class GetMajorTranscriptFromGenomicFeature(Step):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_feature']
    OUT = ['major_transcript']

    def run(self, genomic_feature):
        for feature in genomic_feature:
            res = None
            if feature is not None and len(feature.children) > 0:
                transcripts = sorted(feature.children, key=self.get_transcript_length)
                res = transcripts[-1]
            yield res
        del genomic_feature[:]

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
