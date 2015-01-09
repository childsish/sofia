import bz2
import gzip

from collections import namedtuple
from lhc.itertools.chunked_iterator import ChunkedIterator


FastqEntry = namedtuple('FastqEntry', ('seq_hdr', 'seq', 'qual_hdr', 'qual'))


class FastqEntryIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            gzip.open(fname) if fname.endswith('.gz') else\
            open(fname)
        self.it = ChunkedIterator(self.fhndl, 4)

    def __iter__(self):
        for seq_id, seq, qual_id, qual in self.it:
            yield FastqEntry(seq_id.strip()[1:],
                             seq.strip(),
                             qual_id.strip()[1:],
                             qual.strip())

    def __del__(self):
        if hasattr(self, 'it'):
            self.fhndl.close()
