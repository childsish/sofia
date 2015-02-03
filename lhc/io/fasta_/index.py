import os

from collections import namedtuple
from lhc.filetools.flexible_opener import open_flexibly
from lhc.io.bgzf import get_virtual_offset, BgzfReader


FastaIndexLine = namedtuple('FastaIndexLine', ('length', 'offset', 'n_bases', 'n_bytes'))


class IndexedFastaSet(object):
    def __init__(self, fname):
        self.fname, self.fhndl = open_flexibly(fname, 'rb')
        iname = '{}.fai'.format(fname)
        if not os.path.exists(iname):
            raise ValueError('Fasta index missing. Try: python -m lhc.io.fasta index {}.'.format(fname))
        fhndl = open(iname)
        self.index = {parts[0]: FastaIndexLine(*[int(part) for part in parts[1:]])
                      for parts in (line.strip().split('\t') for line in fhndl)}
        fhndl.close()

    def __len__(self):
        return len(self.index)

    def __getitem__(self, key):
        return IndexedFastaEntry(self.fhndl, self.index[key])

    def fetch(self, chr, start=None, stop=None):
        if start is None and stop is None:
            return IndexedFastaEntry(self.fhndl, self.index[chr])
        start = 0 if start is None else start
        stop = self.index[chr].length if stop is None else stop
        if start > self.index[chr].length or stop > self.index[chr].length:
            raise IndexError('list index out of range')
        offset, length = self.get_offset(chr, start, stop)
        self.fhndl.seek(offset)
        return self.fhndl.read(length).replace('\n', '')

    def get_offset(self, chr, start, stop):
        length, chr_offset, n_bases, n_bytes = self.index[chr]
        start_offset = start + (start / n_bases) * (n_bytes - n_bases)
        stop_offset = stop + (stop / n_bases) * (n_bytes - n_bases)
        length = stop_offset - start_offset
        if self.fname.endswith('gz'):
            start_offset = get_virtual_offset(self.fhndl._handle, start_offset, chr_offset)
            return start_offset, length
        return chr_offset + start_offset, length


class IndexedFastaEntry(object):
    def __init__(self, fhndl, index):
        self.fhndl = fhndl
        self.index = index

    def __str__(self):
        return self[:]

    def __len__(self):
        return self.index.length

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= len(self):
                raise IndexError('list index out of range')
            key = slice(key, key + 1)
        start = 0 if key.start is None else key.start
        stop = len(self) if key.stop is None else key.stop
        offset, length = self.get_offset(start, stop)
        self.fhndl.seek(offset)
        return self.fhndl.read(length).replace('\n', '')

    def get_offset(self, start, stop):
        length, chr_offset, n_bases, n_bytes = self.index
        start_offset = start + (start / n_bases) * (n_bytes - n_bases)
        stop_offset = stop + (stop / n_bases) * (n_bytes - n_bases)
        length = stop_offset - start_offset
        if isinstance(self.fhndl, BgzfReader):
            start_offset = get_virtual_offset(self.fhndl._handle, start_offset, chr_offset)
            return start_offset, length
        return chr_offset + start_offset, length
