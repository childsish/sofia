from collections import namedtuple
from lhc.binf.genomic_coordinate import GenomicInterval as Interval


BedLine = namedtuple('BedLine', ('chr', 'start', 'stop', 'name', 'score', 'strand'))
BedEntry = namedtuple('BedEntry', ('ivl', 'name', 'score'))


class BedLineIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.hdrs, self.line_no = self.parse_headers(self.iterator)
    
    def __del__(self):
        self.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        line = self.iterator.next()
        self.line_no += 1
        if line == '':
            raise StopIteration()
        return self.parse_line(line)

    def seek(self, fpos):
        self.iterator.seek(fpos)

    def close(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()

    @staticmethod
    def parse_headers(fhndl):
        hdrs = []
        line_no = 0
        while True:
            fpos = fhndl.tell()
            line = fhndl.readline()
            if line[:5] not in ('brows', 'track'):
                break
            hdrs.append(line.strip())
            line_no += 1
        fhndl.seek(fpos)
        return hdrs, line_no

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        parts[1] = int(parts[1]) - 1
        parts[2] = int(parts[2])
        return BedLine(*parts)


class BedEntryIterator(BedLineIterator):
    def next(self):
        return self.parse_entry(super(BedEntryIterator, self).next())

    @staticmethod
    def parse_entry(line):
        return BedEntry(Interval(line.chr, line.start, line.stop, line.strand), line.name, line.score)
