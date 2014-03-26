from collections import OrderedDict
from lhc.tools import enum

def iterGenes(fname, it):
    gene = None
    transcript = None
    for row in it(fname):
        if row.type == 'gene':
            if gene is not None:
                yield gene
            gene = Gene(row.attr['ID'], row.ivl)
        elif row.type == 'mRNA':
            transcript = Transcript(row.attr['ID'], row.ivl)
            gene.transcripts[row.attr['ID']] = transcript
        elif row.type in ('CDS', 'five_prime_UTR', 'three_prime_UTR'):
            transcript.exons.append(Exon(row.ivl, row.type))
    yield gene

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
    
    def getBounds(self):
        return self.ivl
