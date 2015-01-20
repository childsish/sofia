from collections import namedtuple
from lhc.binf.genomic_coordinate import Interval
from lhc.filetools.flexible_opener import open_flexibly


BedLine = namedtuple('BedEntry', ('chr', 'start', 'stop', 'name', 'score', 'strand'))
BedEntry = namedtuple('BedEntry', ('ivl', 'name', 'score'))


class BedLineIterator(object):
    def __init__(self, fname):
        self.fname, self.fhndl = open_flexibly(fname)
        self.hdrs, self.line_no = self.parse_headers(self.fhndl)
    
    def __del__(self):
        self.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        line = self.fhndl.next().rstrip('\r\n')
        if line == '':
            raise StopIteration()
        parts = line.split('\t')
        parts[1] = int(parts[1]) - 1
        parts[2] = int(parts[2])
        self.line_no += 1
        return BedLine(*parts)

    def seek(self, fpos):
        self.fhndl.seek(fpos)

    def close(self):
        if hasattr(self.fhndl, 'close'):
            self.fhndl.close()

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


class BedEntryIterator(BedLineIterator):
    def next(self):
        line = super(BedEntryIterator, self).next()
        return BedEntry(Interval(line.chr, line.start, line.stop, line.strand), line.name, line.score)
