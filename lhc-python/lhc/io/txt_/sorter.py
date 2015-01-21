import argparse
import bz2
import os

from functools import partial
from itertools import chain
from lhc.argparse import OpenWritableFile, OpenReadableFile
from lhc.itertools import ChunkedIterator, SortedIteratorMerger
from lhc.io.txt import extract_typed_columns


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
        """
        Get the iterator over the sorted items.

        This function decides whether the items can be sorted in memory or on disk.
        :return:
        """
        lines = self.iterator.next()
        if lines[-1] is None:
            return iter(sorted((line for line in lines if line is not None), key=self.key))
        else:
            import tempfile
            tmp_dir = tempfile.mkdtemp()
            fnames = self._split(tmp_dir, lines)
            return SortedIteratorMerger([open(fname) for fname in fnames], self.key)

    def _split(self, tmp_dir, orig_lines=[]):
        """
        Splits the file into several chunks.

        If the original file is too big to fit in the allocated space, the sorting will be split into several chunks,
        then merged.
        :param tmp_dir: Where to put the intermediate sorted results.
        :param orig_lines: The lines read before running out of space.
        :return: The names of the intermediate files.
        """
        fnames = []
        for i, lines in enumerate(chain([orig_lines], self.iterator)):
            out_fname = os.path.join(tmp_dir, self.TMP_FNAME.format(i + 1))
            self._write(lines, out_fname)
            fnames.append(out_fname)
        return fnames

    def _write(self, lines, fname):
        """
        Writes a intermediate temporary sorted file

        :param lines: The lines to write.
        :param fname: The name of the temporary file.
        :return:
        """
        out_fhndl = open(fname, 'w')
        for line in sorted((line for line in lines if line is not None), key=self.key):
            out_fhndl.write(line)
        out_fhndl.close()


def sort(args):
    types = {
        's': str,
        'f': float,
        'i': int
    }
    columns = [(int(c[0]), types[c[1]]) for c in args.columns]
    typed_column_extractor = partial(extract_typed_columns, columns=columns, sep=args.separator)
    sorter = Sorter(args.input, typed_column_extractor)
    if args.level == 0:
        for line in sorter:
            args.output.write(line)
    else:
        compressor = bz2.BZ2Compressor(args.level)
        for line in sorter:
            args.output.write(compressor.compress(line))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('-c', '--columns', nargs='+',
            help='Which columns and types to extract (default: 1s).')
    add_arg('-i', '--input', action=OpenReadableFile, default=sys.stdin,
            help='The input file (default: stdin).')
    add_arg('-l', '--compresson-level', default=0,
            help='The level of compression from 1-9 (default: 0 - no compression)')
    add_arg('-o', '--output', action=OpenWritableFile, default=sys.stdout,
            help='The output file (default: stdout')
    add_arg('-s', '--separator', default='\t',
            help='The character seperating the columns (default: \\t).')
    parser.set_defaults(func=sort)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
