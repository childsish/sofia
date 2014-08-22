import cPickle

from lhc.binf.genomic_coordinate import Position
from lhc.indices.fasta import FastaIndex

class IndexedFastaFile(object):
    def __init__(self, iname):
        self.iname = iname
        fhndl = open(iname, 'rb')
        self.fname = cPickle.load(fhndl)
        self.index = cPickle.load(fhndl)
        fhndl.close()
        self.fhndl = open(self.fname)
        
        self.prv_key = None
        self.prv_value = None
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __getitem__(self, key):
        if key == self.prv_key:
            return self.prv_value
        self.prv_key = key
        
        if isinstance(key, basestring):
            self.prv_value = IndexedFastaEntry(key, self.fname, self.index)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.index[key]
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in self.index.newlines:
                res = self.fhndl.read(1)
            self.prv_value = res
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self.index[Position(key.chr, key.start)]
            fpos_to = self.index[Position(key.chr, key.stop)]
            self.fhndl.seek(fpos_fr)
            self.prv_value = ''.join(self.fhndl.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return self.prv_value

class IndexedFastaEntry(object):
    def __init__(self, chr, fname, index):
        self.chr = chr
        self.fname = fname
        self.index = index
        self.fhndl = open(fname)
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            fpos = self.index[key]
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in self.index.newlines:
                res = self.fhndl.read(1)
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self.index[Position(self.chr, key.start)]
            fpos_to = self.index[Position(self.chr, key.stop)]
            self.fhndl.seek(fpos_fr)
            res = ''.join(self.fhndl.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return res
    
    def __iter__(self):
        self.fhndl.seek(self.index)
        for line in self.fhndl:
            if line[0] == '>':
                break
            for char in line.strip():
                yield char

class FastaFileIndexer(object):
    def index(self, fname):
        index = FastaIndex(fname)
        infile = open(fname, 'rb')
        fpos = 0
        for line in infile:
            fpos += len(line)
            if line.startswith('>'):
                hdr = line.strip().split()[0][1:]
                index[hdr] = fpos
        return index

