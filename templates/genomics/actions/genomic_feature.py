from sofia_.action import Action


class GetMajorTranscriptFromGenomicFeature(Action):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_feature']
    OUT = ['major_transcript']

    def calculate(self, genomic_feature):
        if genomic_feature is None:
            return None
        genomic_feature = genomic_feature['genomic_feature']
        transcripts = sorted(genomic_feature.children, key=lambda transcript: len(transcript.children))
        return transcripts[-1]
