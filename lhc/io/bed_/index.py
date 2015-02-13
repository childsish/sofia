import os
import warnings

from iterator import BedLineIterator


class IndexedBedFile(object):
    def __init__(self, fname):
        self.fname = fname
        if os.path.exists('{}.tbi'.format(fname)):
            import pysam
            self.index = pysam.Tabixfile(fname)
        elif os.path.exists('{}.lci'.format(fname)):
            import json
            index = json.loads('{}.lci'.format(fname))
        else:
            msg = 'Interval index missing. ' +\
                  'Try: "tabix -p bed {0}" or "python -m lhc.io.bed index {0}".'.format(fname, fname)
            warnings.warn(msg)
            from iterator import BedLineIterator
            from set_ import BedSet
            self.index = BedSet(BedLineIterator(fname))

    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + len(key.ref))
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            lines = self.index.fetch(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for {}'.format(type(key)))
        
        return [BedLineIterator.parse_line(line) for line in lines]
    
    def get_intervals_at_position(self, chr, pos):
        return [BedLineIterator.parse_line(line) for line in self.index.fetch(chr, pos, pos + 1)]
