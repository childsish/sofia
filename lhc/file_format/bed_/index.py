import os
import pysam

from iterator import BedEntryIterator


class IndexedBedFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        iname = '{}.tbi'.format(self.fname)
        if not os.path.exists(iname):
            raise ValueError('File missing interval index. Try: tabix -p bed <FILENAME>.')
        self.index = pysam.Tabixfile(self.fname)

    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + len(key.ref))
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            lines = self.index.fetch(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for {}'.format(type(key)))
        
        return [BedEntryIterator._parse_line(line) for line in lines]
    
    def get_intervals_at_position(self, chr, pos):
        return [BedEntryIterator._parse_line(line) for line in self.index.fetch(chr, pos, pos + 1)]
