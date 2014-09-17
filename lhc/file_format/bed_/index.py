import os
import pysam

from iterator import BedIterator

class IndexedBedFile(object):
    def __init__(self, iname):
        self.iname = iname
        self.fname = os.path.abspath(iname)[:-4]
        self.index = pysam.Tabixfile(self.fname)

    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + len(key.ref))
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            lines = self.index.fetch(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        
        return [BedIterator._parseLine(line) for line in lines]
