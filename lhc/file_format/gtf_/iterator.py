import bz2
import gzip

from collections import namedtuple
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.genomic_coordinate import Interval
from lhc.collections import SortedValueDict


GtfLine = namedtuple('GtfLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))


class GtfLineIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)
        self.hdr = self.parse_header(self.fhndl)

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        return self.parse_line(self.fhndl.next())

    def close(self):
        if hasattr(self.fhndl, 'close'):
            self.fhndl.close()

    @staticmethod
    def parse_header(fhndl):
        hdrs = []
        while True:
            pos = fhndl.tell()
            line = fhndl.readline()
            if not line.startswith('#'):
                break
            hdrs.append(line.strip())
        fhndl.seek(pos)
        return hdrs

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        parts[3] = int(parts[3]) - 1
        parts[4] = int(parts[4])
        parts[8] = GtfLineIterator.parse_attributes(parts[8])
        return GtfLine(*parts)

    @staticmethod
    def parse_attributes(attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)


class GtfEntityIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.it = GtfLineIterator(fname)
        self.genes = SortedValueDict(key=lambda item: (item[0].chr, item[0].stop))
    
    def __iter__(self):
        return self

    def next(self):
        """
        New method does not assume that genes are ordered, only that the intervals are ordered. This should work for
        both original gtf files (ordered by gene) and gtf files ordered by interval for indexing.
        :return: GeneModel
        """
        for line in self.it:
            gene = None
            lowest_gene_name, (lowest_interval, lowest_lines) = self.genes.peek_lowest()
            if line.chr != lowest_interval.chr or line.start > lowest_interval.stop:
                self.genes.pop_lowest()
                gene = self.parse_gene(lowest_gene_name, lowest_interval, lowest_lines)

            gene_name = line.attr['gene_name']
            if gene_name not in self.genes:
                interval = Interval(line.chr, line.start, line.stop, line.strand)
                lines = [line]
            else:
                interval, lines = self.genes[gene_name]
                interval.union(Interval(line.chr, line.start, line.stop, line.strand))
                lines.append(line)
                del self.genes[gene_name]
            self.genes[gene_name] = (interval, lines)

            if gene is not None:
                return gene
        lowest_gene_name, (lowest_interval, lowest_lines) = self.genes.pop_lowest()
        return self.parse_gene(lowest_gene_name, lowest_interval, lowest_lines)

    @staticmethod
    def parse_gene(name, interval, lines):
        gene = Gene(name, interval)

        gene_name = line.attr['gene_name']
        if gene_name not in self.genes:
            self.genes[gene_name] = (Interval(line.chr, line.start, line.stop), [])

        if line.type == 'gene':
            gene = Gene(line.attr['gene_name'])
            break
        for line in self.it:
            ivl = Interval(line.chr, int(line.start) - 1, int(line.stop), line.strand)
            attr = self._parse_attributes(line.attr)
            if line.type == 'gene':
                gene = Gene(attr(['gene_name']))
            elif line.type == 'transcript':
                transcript_name = attr['transcript_name']
                gene.transcripts[transcript_name] = Transcript(transcript_name, ivl)
            elif line.type == 'CDS':
                transcript_name = attr['transcript_name']
                gene.transcripts[transcript_name].exons.append(Exon(ivl, 'CDS'))
        return gene

    def __del__(self):
        if hasattr(self, 'it'):
            self.it.close()
