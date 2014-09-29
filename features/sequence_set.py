from ebias.feature import Feature

class GetCodingSequenceByGeneModel(Feature):

    IN = ['chromosome_sequence_set', 'major_transcript']
    OUT = ['coding_sequence']

    def calculate(self, chromosome_sequence_set, major_transcript):
        if major_transcript is None:
            return None
        return major_transcript.getSubSeq(chromosome_sequence_set)#, type='CDS')
