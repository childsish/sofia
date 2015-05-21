import argparse

from csv_.iterator import CsvIterator
from csv_ import sort


def iter_csv(fname, entry=None, comment='#', skip=0, delimiter='\t'):
    yield CsvIterator(fname, entry, comment, skip, delimiter)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    sort_parser = subparsers.add_parser('sort')
    sort.define_parser(sort_parser)

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
