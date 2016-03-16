from collections import namedtuple
from lhc.itertools.chunked_iterator import ChunkedIterator


class FastqEntry(namedtuple('FastqEntry', ('hdr', 'seq', 'qual_hdr', 'qual'))):
    def __str__(self):
        return '@{}\n{}\n{}+\n{}\n'.format(self.hdr, self.seq, self.qual_hdr, self.qual)


class FastqEntryIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.it = ChunkedIterator(self.iterator, 4)

    def __iter__(self):
        return self

    def next(self):
        seq_id, seq, qual_id, qual = self.it.next()
        return FastqEntry(seq_id.strip()[1:],
                          seq.strip(),
                          qual_id.strip()[1:],
                          qual.strip())

    def __del__(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()
