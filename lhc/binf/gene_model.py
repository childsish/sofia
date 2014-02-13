class TranscriptModel(object):
    def __init__(self, ivls=[]):
        self.ivls = ivls
    
    def getSubSeq(self, seq):
        return ''.join([ivl.getSubSeq(seq) for ivl in self.ivls])

class GeneModel(object):
    def __init__(self, name, ivl):
        self.name = name
        self.ivl = ivl
        self.transcripts = {}
