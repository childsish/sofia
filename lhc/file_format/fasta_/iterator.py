import bz2
import gzip

from collections import namedtuple
from lhc.filetools.flexible_opener import open_flexibly


class FastaEntry(namedtuple('FastaEntry', ('hdr', 'seq'))):
    def __str__(self):
        """
        Represent the entry as a string. Only intended for entries with short sequences.

        :return: The fasta entry as a string
        """
        return '{}\n{}\n'.format(self.hdr, self.seq)


class FastaEntryIterator(object):
    def __init__(self, fname, hdr_parser=None):
        self.fname, self.fhndl = open_flexibly(fname)
        self.hdr_parser = (lambda x:x) if hdr_parser is None else hdr_parser
        self.line = self.fhndl.next()
    
    def __iter__(self):
        return self

    def next(self):
        if self.line is None:
            raise StopIteration()

        seq = []
        for line in self.fhndl:
            if line.startswith('>'):
                hdr = self.hdr_parser(self.line[1:].strip())
                self.line = line
                return FastaEntry(hdr, ''.join(seq))
            seq.append(line.strip())
        hdr = self.hdr_parser(self.line[1:].strip())
        self.line = None
        return FastaEntry(hdr, ''.join(seq))

    def __del__(self):
        if hasattr(self.fhndl, 'close'):
            self.fhndl.close()
