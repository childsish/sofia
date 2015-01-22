import gzip

from collections import namedtuple
from itertools import chain, izip, tee


SamLine = namedtuple('SamLine', ('qname', 'flag', 'rname', 'pos', 'mapq', 'cigar', 'rnext', 'pnext', 'tlen', 'seq',
                                 'qual'))


class BamLineIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.iterator = pairwise(gzip.open(fname) if fname.endswith('.bam') else open(fname))
        self.hdrs, self.line_no = self.parse_headers(self.iterator)

    def __iter__(self):
        return self

    def next(self):
        line, next_line = self.iterator.next()
        self.line_no += 1
        return self.parse_line(line)

    @staticmethod
    def parse_headers(pairwise_iterator):
        hdrs = []
        for line_no, (line, next_line) in enumerate(pairwise_iterator):
            hdrs.append(line)
            if not next_line.startswith('@'):
                break
        return hdrs, line_no

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        parts[3] = int(parts[3]) - 1
        return SamLine(*parts)


def pairwise(iterable):
    a, b = tee(iterable)
    b = chain(b, [None])
    b.next()
    return izip(a, b)
