from collections import OrderedDict
from lhc.tools import enum

class Gene(object):
    def __init__(self, name, ivl, transcripts=None):
        self.name = name
        self.ivl = ivl
        self.transcripts = OrderedDict() if transcripts is None else transcripts

class Transcript(object):
    def __init__(self, name, ivl, exons=None):
        self.name = name
        self.ivl = ivl
        self.exons = [] if exons is None else exons
    
    def getSubSeq(self, seq, valid_types=set(['CDS', 'UTR5', 'UTR3'])):
        return ''.join([exon.getSubSeq(seq) for exon in self.exons if exon.type in valid_types])

class Exon(object):
    
    TYPE = enum(['gene', 'transcript', 'CDS', 'UTR5', 'UTR3'])
    
    def __init__(self, ivl, type_):
        self.ivl = ivl
        self.type = type_
    
    def getSubSeq(self, seq):
        return self.ivl.getSubSeq(seq)
