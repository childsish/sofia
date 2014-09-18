import os

from lhc.binf.genomic_coordinate import Position

class IndexedFastaFile(object):
    def __init__(self, fname):
        if fname.endswith('.gz'):
            raise NotImplementedError('Unable to handle bgzipped fasta files, yet...')
        self.fname = os.path.abspath(fname)
        iname = '%s.fai'%self.fname
        if not os.path.exists(iname):
            raise ValueError('File missing fasta index. Try: samtools faidx <FILENAME>.')
        fhndl = open(iname)
        self.index = dict((parts[0], [int(part) for part in parts[1:]]) for parts in\
            (line.strip().split('\t') for line in fhndl))
        fhndl.close()
        self.fhndl = open(self.fname, 'rb') if fname.endswith('.rz') else open(self.fname)
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            self.prv_value = IndexedFastaEntry(key, self.fname, self.index)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self._getFilePosition(key.chr, key.pos)
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in '\r\n':
                res = self.fhndl.read(1)
            self.prv_value = res
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self._getFilePosition(key.chr, key.start)
            fpos_to = self._getFilePosition(key.chr, key.stop)
            self.fhndl.seek(fpos_fr)
            self.prv_value = ''.join(self.fhndl.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return self.prv_value

    def _getFilePosition(self, chr, pos):
        length, offset, n_bases, n_bytes = self.index[chr]
        return offset + pos + (pos / n_bytes) * (n_bytes - n_bases)

class IndexedFastaEntry(object):
    def __init__(self, chr, fname, index):
        self.chr = chr
        self.fname = fname
        self.index = index
        self.fhndl = open(fname)
    
    def __str__(self):
        length, offset, n_bases, n_bytes = self.index[self.chr]
        self.fhndl.seek(offset)
        return self.fhndl.read(length + length / n_bases).replace('\n', '')
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            fpos = self._getFilePosition(self.chr, key)
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in self.index.newlines:
                res = self.fhndl.read(1)
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self._getFilePosition(self.chr, key.start)
            fpos_to = self._getFilePosition(self.chr, key.stop)
            self.fhndl.seek(fpos_fr)
            res = self.fhndl.read(fpos_to - fpos_fr).split().replace('\n', '')
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

    def _getFilePosition(self, chr, pos):
        length, offset, n_bases, n_bytes = self.index[chr]
        return offset + pos + (pos / n_bytes) * (n_bytes - n_bases)

