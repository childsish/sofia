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

    def getMajorTranscript(self):
        return sorted(self.transcripts.itervalues(), key=lambda x:len(x))[-1]

    def __str__(self):
        return '%s:%s'%(self.name, str(self.ivl))

class Transcript(object):
    def __init__(self, name, ivl, exons=None):
        self.name = name
        self.ivl = ivl
        self.exons = [] if exons is None else exons

    def __str__(self):
        return '%s:%s'%(self.name, str(self.ivl))
    
    def __len__(self):
        return sum(map(len, self.exons))

    def getRelPos(self, pos):
        rel_pos = 0
        for exon in self.exons:
            if exon.ivl.start <= pos and exon.ivl.stop > pos:
                return rel_pos + exon.get_rel_pos(pos)
            rel_pos += len(exon)
        return None
        #raise IndexError('Position %s not in %s'%(pos, self.name))
    
    def getSubSeq(self, seq, fr=None, to=None, valid_types=set(['CDS', 'UTR5', 'UTR3'])):
        return ''.join([exon.get_sub_seq(seq, fr, to)\
            for exon in self.exons if exon.type in valid_types])
    
class Exon(object):
    
    TYPE = enum(['gene', 'transcript', 'CDS', 'UTR5', 'UTR3'])
    
    def __init__(self, ivl, type_):
        self.ivl = ivl
        self.type = type_
    
    def __str__(self):
        return '%s..%s'%(self.ivl.start, self.ivl.stop)
    
    def __len__(self):
        return len(self.ivl)
    
    def getSubSeq(self, seq, fr=None, to=None):
        return self.ivl.get_sub_seq(seq, fr, to)

    def getRelPos(self, pos):
        return self.ivl.get_rel_pos(pos)

