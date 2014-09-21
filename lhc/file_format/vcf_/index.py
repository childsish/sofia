import os
import pysam

from iterator import VcfIterator

class IndexedVcfFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        iname = '%s.tbi'%self.fname
        if not os.path.exists(iname):
            raise ValueError('File missing interval index. Try: tabix -p vcf <FILENAME>.')
        self.index = pysam.Tabixfile(self.fname)
        self.iterator = VcfIterator(self.fname)
    
    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + len(key.ref))
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            lines = self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            lines = self.index.fetch(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        
        return [self.iterator._parseLine(line) for line in lines]
