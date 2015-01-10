import bz2
import gzip

from collections import namedtuple

BedEntry = namedtuple('BedEntry', ('chr', 'start', 'stop', 'name', 'score', 'strand'))


class BedEntryIterator(object):
    # TODO: Implement BED headers
    
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)
        self.line_no = 0
        self.hdrs = self._parse_headers()
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        line = self.fhndl.next().strip('\r\n')
        if line == '':
            raise StopIteration()
        parts = line.split('\t')
        parts[1] = int(parts[1]) - 1
        parts[2] = int(parts[2])
        self.line_no += 1
        return BedEntry(*parts)

    def seek(self, fpos):
        self.fhndl.seek(fpos)

    def _parse_headers(self):
        hdrs = []
        while True:
            fpos = self.fhndl.tell()
            line = self.fhndl.readline()
            if line[:5] not in ('brows', 'track'):
                break
            hdrs.append(line.strip())
            self.line_no += 1
        self.fhndl.seek(fpos)
        return hdrs
