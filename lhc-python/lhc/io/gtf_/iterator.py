from collections import namedtuple
from lhc.binf.genomic_feature import GenomicFeature
from lhc.binf.genomic_coordinate import Interval
from lhc.collections import SortedValueDict
from lhc.filetools.flexible_opener import open_flexibly


GtfLine = namedtuple('GtfLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))


class GtfLineIterator(object):
    def __init__(self, fname):
        self.fname, self.fhndl = open_flexibly(fname)
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
        passed_lowest = False
        for line in self.it:
            try:
                lowest_gene_name, (lowest_interval, lowest_lines) = self.genes.peek_lowest()
                passed_lowest = line.chr != lowest_interval.chr or line.start > lowest_interval.stop
            except IndexError:
                pass

            gene_name = line.attr['gene_name']
            if gene_name not in self.genes:
                self.genes[gene_name] = (Interval(line.chr, line.start, line.stop, line.strand), [line])
            else:
                interval, lines = self.genes[gene_name]
                interval.get_value().union(Interval(line.chr, line.start, line.stop, line.strand))
                lines.get_value().append(line)

            if passed_lowest:
                break
        try:
            lowest_gene_name, (lowest_interval, lowest_lines) = self.genes.pop_lowest()
        except IndexError:
            raise StopIteration
        return self.parse_gene(lowest_lines)[0]

    def close(self):
        self.it.close()

    @staticmethod
    def parse_gene(lines):
        top_features = {}
        open_features = {}
        for line in sorted(lines, key=lambda line: (line.start, -line.stop)):
            interval = Interval(line.chr, line.start, line.stop, line.strand)
            if line.type == 'gene':
                gene_name = line.attr['gene_name']
                feature = GenomicFeature(gene_name, 'gene', interval, line.attr)
                top_features[gene_name] = feature
            elif line.type == 'transcript':
                gene_name = line.attr['gene_name']
                transcript_name = line.attr['transcript_name']
                feature = GenomicFeature(transcript_name, 'transcript', interval, line.attr)
                top_features[gene_name].add_child(feature)
                open_features[transcript_name] = feature
            elif line.type == 'CDS':
                transcript_name = line.attr['transcript_name']
                feature = GenomicFeature(interval, 'CDS', interval, line.attr)
                open_features[transcript_name].add_child(feature)
        return top_features.values()

    def __del__(self):
        self.close()
