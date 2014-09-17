import gzip

from collections import namedtuple
from lhc.binf.genomic_coordinate import Interval

BedEntry = namedtuple('BedEntry', ('chr', 'start', 'stop', 'name', 'score', 'strand'))

class BedIterator(object):
    #TODO: Implemented BED headers
    
    CHR = 0
    START = 1
    STOP = 2
    NAME = 3
    SCORE = 4
    STRAND = 5
    
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        line = self.fhndl.next()
        while line[:5] in ['brows', 'track']: #TODO: remove when bed headers implemented
            line = self.fhndl.next()
        return self._parseLine(line)

    def seek(self, fpos):
        self.fhndl.seek(fpos)

    @classmethod
    def _parseLine(cls, line):
        parts = line.strip().split('\t')
        return BedEntry(parts[cls.CHR],
            int(parts[cls.START]) - 1,
            int(parts[cls.STOP]),
            parts[cls.NAME],
            parts[cls.SCORE],
            parts[cls.STRAND])
 