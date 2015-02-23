import gzip

from collections import namedtuple
from itertools import chain, izip, tee


sam_line_headers = ('qname', 'flag', 'rname', 'pos', 'mapq', 'cigar', 'rnext', 'pnext', 'tlen', 'seq', 'qual', 'tags')
class SamLine(namedtuple('SamLine', sam_line_headers)):
    def __str__(self):
        return '{0.qname}\t{0.flag}\t{0.rname}\t{1}\t{0.mapq}\t{0.cigar}\t{0.rnext}\t{0.pnext}\t{0.tlen}\t{0.seq}\t{0.qual}\t{0.tags}'.format(self, self.pos + 1)


class SamLineIterator(object):
    def __init__(self, fname):
        if isinstance(fname, file):
            self.fname = fname.name
            it = fname
        else:
            self.fname = fname
            it = gzip.open(fname) if fname.endswith('.bam') else\
                open(fname)
        self.iterator = pairwise(it)
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
        line_no = 0
        for line_no, (line, next_line) in enumerate(pairwise_iterator):
            hdrs.append(line.rstrip('\r\n'))
            if not next_line.startswith('@'):
                break
        return hdrs, line_no

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t', 11)
        parts[3] = int(parts[3]) - 1
        parts[4] = int(parts[4])
        parts[8] = int(parts[8])
        
        return SamLine(*parts)


def pairwise(iterable):
    a, b = tee(iterable)
    b = chain(b, [None])
    b.next()
    return izip(a, b)
