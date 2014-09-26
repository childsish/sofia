import os
import pysam

from lhc.binf.genomic_coordinate import Position

class IndexedFastaFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        iname1 = '%s.fai'%self.fname
        iname2 = '%s.bzi'%self.fname
        if not (os.path.exists(iname1) and os.path.exists(iname1)):
            raise ValueError('File missing fasta index. Try: samtools faidx <FILENAME>.')
        self.index = pysam.Fastafile(fname)
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            return IndexedFastaEntry(key, self.index)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.getInterval(key.chr, key.start, key.stop)
        raise NotImplementedError('Random access not implemented for %s'%type(key))

    def getInterval(self, chr, start, stop):
        return self.index.fetch(chr, start, stop)

class IndexedFastaEntry(object):
    def __init__(self, chr, index):
        self.chr = chr
        self.index = index
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.index.fetch(self.chr, key, key + 1)
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.index.fetch(self.chr, key.start, key.stop)
        raise NotImplementedError('Random access not implemented for %s'%type(key))
