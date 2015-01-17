import bz2
import gzip

from collections import namedtuple
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.genomic_coordinate import Interval


GtfLine = namedtuple('GtfLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))


class GtfLineIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)

    def __iter__(self):
        fhndl = self.fhndl
        for line in fhndl:
            if line.startswith('#'):
                continue
            yield self.parse(line)
    
    @staticmethod
    def parse(line):
        return GtfLine(*line.strip().split('\t'))

    def close(self):
        if hasattr(self, 'fhndl'):
            self.fhndl.close()

    def __del__(self):
        self.close()


class GtfEntityIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.it = GtfLineIterator(fname)
    
    def __iter__(self):
        for line in self.it:
            if line.type == 'gene':
                gene = Gene(line.attr['gene_name'])
                break
        for line in self.it:
            ivl = Interval(line.chr, int(line.start) - 1, int(line.stop), line.strand)
            attr = self._parse_attributes(line.attr)
            if line.type == 'gene':
                yield gene
                gene = Gene(attr(['gene_name']))
            elif line.type == 'transcript':
                transcript_name = attr['transcript_name']
                gene.transcripts[transcript_name] = Transcript(transcript_name, ivl)
            elif line.type == 'CDS':
                transcript_name = attr['transcript_name']
                gene.transcripts[transcript_name].exons.append(Exon(ivl, 'CDS'))
        yield gene
    
    @staticmethod
    def _parse_attributes(attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)

    def __del__(self):
        if hasattr(self, 'it'):
            self.it.close()
