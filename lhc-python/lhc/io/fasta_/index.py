import json
import os

from Bio import bgzf
from Bio.bgzf import make_virtual_offset, _load_bgzf_block
from lhc.io.txt_.index import FileIndex


class IndexedFastaSet(object):
    def __init__(self, fname):
        self.fname = fname
        if not os.path.exists('{}.lci'.format(fname)):
            msg = 'Interval index missing. Try: "python -m lhc.io.fasta index {}".'.format(fname)
            raise OSError(msg)
        self.fhndl = bgzf.open(fname)
        fhndl = open('{}.lci'.format(fname))
        self.index = FileIndex.init_from_state(json.load(fhndl))
        fhndl.close()

        for line in self.fhndl:
            if not line.startswith('>'):
                break
        self.width = len(line.strip())

    def __len__(self):
        return len(self.index.keys)

    def __getitem__(self, key):
        return IndexedFastaEntry(self.fhndl, self.index, key, self.width)

    def fetch(self, chr, start, stop):
        return self[chr].fetch(start, stop)


class IndexedFastaEntry(object):
    def __init__(self, fhndl, index, chr, width):
        self.fhndl = fhndl
        self.index = index
        self.chr = chr
        self.width = width

    def __str__(self):
        return self[:]

    def __getitem__(self, key):
        if isinstance(key, int):
            key = slice(key, key + 1)
        return self.fetch(key.start, key.stop)

    def fetch(self, start, stop):
        block_start, length, hdr = self.index[(self.chr, start)]
        fr_chr, fr_start = self.index.get_key_below((self.chr, start))

        offset = start - fr_start
        virtual_offset = block_start + hdr + offset + offset / self.width
        self.fhndl.seek(virtual_offset)
        return self.fhndl.read(stop - start + (stop - start) / self.width).replace('\n', '')
