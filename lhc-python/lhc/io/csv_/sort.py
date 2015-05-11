import argparse
import os
import re
import time

from itertools import chain
from lhc.itertools import ChunkedIterator, SortedIteratorMerger


class CsvSorter(object):

    TMP_FNAME = '{}.txt'

    def __init__(self, fhndl, format, max_lines=1000000, delimiter='\t'):
        def key(line):
            parts = line.split(delimiter)
            return tuple(type_(parts[column]) for type_, column in format)

        self.key = key
        self.iterator = ChunkedIterator(fhndl, max_lines)
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
        lines = list(self.iterator.next())
        if len(lines) < self.iterator.chunk:
            return iter(sorted(lines, key=self.key))

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
            lines = list(lines)
            out_fname = os.path.join(tmp_dir, self.TMP_FNAME.format(i + 1))
            self._write(lines, out_fname)
            fnames.append(out_fname)
            if len(lines) < self.iterator.chunk:
                break
        return fnames

    def _write(self, lines, fname):
        """
        Writes a intermediate temporary sorted file

        :param lines: The lines to write.
        :param fname: The name of the temporary file.
        :return:
        """
        out_fhndl = open(fname, 'w')
        for line in sorted(lines, key=self.key):
            out_fhndl.write(line)
        out_fhndl.close()


def sort(args):
    import sys

    format = [parse_format(format) for format in args.format]
    in_fhndl = sys.stdin if args.input is None else open(args.input)
    out_fhndl = sys.stdout if args.output is None else open(args.output, 'w')

    start = time.time()
    sorter = CsvSorter(in_fhndl, format=format, max_lines=args.max_lines, delimiter=args.delimiter)
    for i, line in enumerate(sorter):
        out_fhndl.write(line)
    duration = time.time() - start

    out_fhndl.close()
    n_tmp = ' ' + str(len(sorter.sorted_iterator.iterators)) if hasattr(sorter.sorted_iterator, 'iterators') else ''
    negator = ' without' if n_tmp == '' else ''
    plural = '' if n_tmp == 1 else 's'
    sys.stderr.write('Sorted {} lines in {:.3f} seconds{} using{} temporary file{}.\n'.format(i, duration, negator, n_tmp, plural))


def parse_format(format):
    regx = re.compile('(?P<code>\w+)(?P<column>\d+)')
    types = {'s': str, 'i': int, 'f': float}
    match = regx.match(format)
    return types[match.group('code')], int(match.group('column')) - 1


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', default=None, nargs='?',
            help='The input file (default: stdin).')
    add_arg('output', default=None, nargs='?',
            help='The output file (default: stdout')
    add_arg('-f', '--format', nargs='+', default=['s1'],
            help='Which columns and types to extract (default: s1).')
    add_arg('-s', '--delimiter', default='\t',
            help='The character delimiting the columns (default: \\t).')
    add_arg('-m', '--max-lines', default=1000000, type=int,
            help='The maximum number of lines to sort simultaneously')
    parser.set_defaults(func=sort)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
