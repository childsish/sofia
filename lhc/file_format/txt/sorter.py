import argparse
import os

from itertools import chain
from lhc.itertools import ChunkedIterator, SortedIteratorMerger


def default_key(line):
    return line


class Sorter(object):

    TMP_FNAME = '{}.txt'

    def __init__(self, iterator, key=default_key, max_lines=2 ** 16):
        self.key = key
        self.iterator = ChunkedIterator(iterator, max_lines)
        self.sorted_iterator = self._get_sorted_iterator()

    def __iter__(self):
        return self

    def next(self):
        return self.sorted_iterator.next()

    def _get_sorted_iterator(self):
        lines = self.iterator.next()
        if lines[-1] is None:
            return iter(sorted((line for line in lines if line is not None), key=self.key))
        else:
            import tempfile
            tmp_dir = tempfile.mkdtemp()
            fnames = self._split(tmp_dir, lines)
            return SortedIteratorMerger([open(fname) for fname in fnames], self.key)

    def _split(self, tmp_dir, orig_lines=[]):
        fnames = []
        for i, lines in enumerate(chain([orig_lines], self.iterator)):
            out_fname = os.path.join(tmp_dir, self.TMP_FNAME.format(i + 1))
            self._write(lines, out_fname)
            fnames.append(out_fname)
        return fnames

    def _write(self, lines, fname):
        out_fhndl = open(fname, 'w')
        for line in sorted((line for line in lines if line is not None), key=self.key):
            out_fhndl.write(line)
        out_fhndl.close()


def sort():
    pass


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
