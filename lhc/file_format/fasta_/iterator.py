import bz2
import gzip

from collections import namedtuple


class FastaEntry(namedtuple('FastaEntry', ('hdr', 'seq'))):
    def __str__(self):
        """
        Represent the entry as a string. Only intended for entries with short sequences.

        :return: The fasta entry as a string
        """
        return '{}\n{}\n'.format(self.hdr, self.seq)


class FastaEntryIterator(object):
    def __init__(self, fname, hdr_parser=None):
        self.fname = fname
        self.fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)
        self.hdr_parser = (lambda x:x) if hdr_parser is None else hdr_parser

    def close(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        hdr_parser = self.hdr_parser
        for line in self.fhndl:
            if line.startswith('>'):
                hdr = hdr_parser(line[1:].strip())
                break
        seq = []
        for line in self.fhndl:
            if line.startswith('>'):
                yield FastaEntry(hdr, ''.join(seq))
                hdr = hdr_parser(line[1:].strip())
                seq = []
            else:
                seq.append(line.strip())
        yield FastaEntry(hdr, ''.join(seq))

    def __del__(self):
        self.close()
