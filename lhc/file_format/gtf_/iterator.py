from collections import namedtuple
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.genomic_coordinate import Interval

GtfEntry = namedtuple('GtfEntry', ('chr', 'src', 'type', 'start', 'stop',
    'score', 'strand', 'phase', 'attr'))

class GtfIterator(object):
    
    CHR = 0
    SRC = 1
    TYPE = 2
    START = 3
    STOP = 4
    SCORE = 5
    STRAND = 6
    PHASE = 7
    ATTR = 8
    
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = open(fname)
        self._initGene()
    
    def __del__(self):
        if not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.gene is None:
            raise StopIteration()
        res = None
        for line in self.fhndl:
            type, ivl, attr = self._parseLine(line)
            if type == 'gene':
                res = self.gene
                self.gene = Gene(attr['gene_name'], ivl)
                break
            elif type == 'transcript':
                self.gene.transcripts[attr['transcript_name']] =\
                    Transcript(attr['transcript_name'], ivl)
            elif type == 'CDS':
                self.gene.transcripts[attr['transcript_name']].exons.append(Exon(ivl, 'CDS'))
        if res is None:
            res = self.gene
            self.gene = None
        return res
    
    def seek(self, fpos):
        self.fhndl.seek(fpos)
        line = self.fhndl.next()
        type, ivl, attr = self._parseLine(line)
        while type != 'gene':
            line = self.fhndl.next()
            type, ivl, attr = self._parseLine(line)
        self.gene = Gene(attr['gene_name'], ivl)
    
    def _parseLine(self, line):
        parts = line.strip().split('\t')
        ivl = Interval(parts[self.CHR], int(parts[self.START]) - 1, int(parts[self.STOP]))
        attr = self._parseAttributes(parts[self.ATTR])
        return parts[self.TYPE], ivl, attr
    
    def _parseAttributes(self, attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)
