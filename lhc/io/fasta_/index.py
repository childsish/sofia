import argparse
import os

from collections import namedtuple
from lhc.filetools.flexible_opener import open_flexibly


FastaIndex = namedtuple('FastaIndex', ('length', 'offset', 'n_bases', 'n_bytes'))


class FastaIndexer(object):
    def __init__(self, fname, key=lambda line: line.split()[0]):
        self.fname, self.fhndl = open_flexibly(fname, 'rb')
        self.key = key
        self.line = self.readline()
        self.offset = self.fhndl.tell()
        self.n_bytes, self.n_bases = self.get_width()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        if self.line == '':
            raise StopIteration()

        length = self.n_bases
        line = self.readline()
        while line != '' and not line.startswith('>'):
            length += len(line.strip())
            line = self.readline()
        hdr = self.key(self.line.strip().split()[0])
        offset = self.offset
        self.offset = self.fhndl.tell()
        self.line = line
        return hdr[1:], length, offset, self.n_bases, self.n_bytes

    def readline(self):
        try:
            return self.fhndl.readline()
        except RuntimeError, e:
            raise RuntimeError('{}\nIf a RuntimeError has occurred, '.format(e) +
                               'the sequences may not be split over several lines. ' +
                               'Try: python -m lhc.io.fasta wrap {}'.format(self.fname))

    def get_width(self):
        line = self.readline()
        n_bytes = len(line)
        n_bases = len(line.strip())
        return n_bytes, n_bases

    def close(self):
        if hasattr(self.fhndl, 'close'):
            self.fhndl.close()


class IndexedFastaSet(object):
    def __init__(self, fname):
        self.fname, self.fhndl = open_flexibly(fname, 'rb')
        iname = '{}.fai'.format(fname)
        if not os.path.exists(iname):
            raise ValueError('File missing fasta index. Try: python -m lhc.io.fasta index {}.'.format(fname))
        fhndl = open(iname)
        self.index = {parts[0]: FastaIndex(*[int(part) for part in parts[1:]])
                      for parts in (line.strip().split('\t') for line in fhndl)}
        fhndl.close()

    def __getitem__(self, key):
        return IndexedFastaEntry(self.index[key], self.fhndl)

    def get_position(self, chr, pos):
        if pos >= self.index[chr].length:
            raise IndexError('list index out of range')
        offset = self.get_offset(chr, pos)
        self.fhndl.seek(offset)
        return self.fhndl.read(1)

    def get_interval(self, chr, start, stop):
        offset = self.get_offset(chr, start)
        length = self.get_offset(chr, stop) - offset
        self.fhndl.seek(offset)
        return self.fhndl.read(length).replace('\n', '')

    def get_offset(self, chr, pos):
        length, offset, n_bases, n_bytes = self.index[chr]
        return offset + pos + (pos / n_bases) * (n_bytes - n_bases)


class IndexedFastaEntry(object):
    def __init__(self, index, fhndl):
        self.index = index
        self.fhndl = fhndl

    def __str__(self):
        return self[:]

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= len(self):
                raise IndexError('list index out of range')
            key = slice(key, key + 1)
        offset = self.get_offset(0 if key.start is None else key.start)
        length = self.get_offset(len(self) if key.stop is None else key.stop) - offset
        self.fhndl.seek(offset)
        return self.fhndl.read(length).replace('\n', '')

    def __len__(self):
        return self.index.length

    def get_offset(self, pos):
        length, offset, n_bases, n_bytes = self.index
        return offset + pos + (pos / n_bytes) * (n_bytes - n_bases)


def index(input, extension='.fai'):
    out_fhndl = open('{}{}'.format(input, extension), 'w')
    indexer = FastaIndexer(input)
    for hdr, length, offset, n_bases, n_bytes in indexer:
        out_fhndl.write('{}\t{}\t{}\t{}\t{}\n'.format(hdr, length, offset, n_bases, n_bytes))
    out_fhndl.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', help='The input fasta file.')
    add_arg('-e', '--extension', default='.fai',
            help='The extension of the index file (default: .fai).')
    parser.set_defaults(func=lambda args: index(args.input, args.extenson))
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
