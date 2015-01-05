import gzip

from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.genomic_coordinate import Interval


class GtfEntityIterator(object):
    
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
        self.fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
        self.seek(0)
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.gene is None:
            raise StopIteration()
        res = None
        for line in self.fhndl:
            if line.startswith('#'):
                continue
            type, ivl, attr = self._parse_line(line)
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
        while line[0] == '#':
            line = self.fhndl.next()
        type, ivl, attr = self._parse_line(line)
        while type != 'gene':
            line = self.fhndl.next()
            type, ivl, attr = self._parse_line(line)
        self.gene = Gene(attr['gene_name'], ivl)
    
    @classmethod
    def _parse_line(cls, line):
        parts = line.strip().split('\t')
        ivl = Interval(parts[cls.CHR], int(parts[cls.START]) - 1, int(parts[cls.STOP]), parts[cls.STRAND])
        attr = cls._parse_attributes(parts[cls.ATTR])
        return parts[cls.TYPE], ivl, attr
    
    @classmethod
    def _parse_attributes(cls, attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)
