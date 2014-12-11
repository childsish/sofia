from sofia_.action import Action


class GetCodingSequenceByGeneModel(Action):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set)#, type='CDS')


class GetFivePrimeUtr(Action):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['five_prime_utr']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set, type="5'UTR5")


class GetThreePrimeUtr(Action):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['three_prime_utr']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set, type="3'UTR")
