from sofia.step import Step, EndOfStream


class GetMajorTranscriptFromGenomicFeature(Step):
    """
    Get the major transcript of a genomic feature. Defined as the longest transcript (ie. most complete).
    """

    IN = ['genomic_feature']
    OUT = ['major_transcript']

    def run(self, ins, outs):
        while len(ins) > 0:
            genomic_feature = ins.genomic_feature.pop()
            if genomic_feature is EndOfStream:
                outs.major_transcript.push(EndOfStream)
                return True

            major_transcript = sorted(genomic_feature.children, key=self.get_transcript_length)[-1]
            if not outs.major_transcript.push(major_transcript):
                break
        return len(ins) == 0

    @staticmethod
    def get_transcript_length(transcript):
        return sum(len(child) for child in transcript.children if child.type == 'CDS')
