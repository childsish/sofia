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
        genomic_feature = genomic_feature['data']
        mx_exon = 0
        mx_transcript = None
        for transcript in genomic_feature.children:
            n_exon = sum(child.type == 'exon' for child in transcript.children)
            if n_exon > mx_exon:
                mx_exon = n_exon
                mx_transcript = transcript
        return mx_transcript
