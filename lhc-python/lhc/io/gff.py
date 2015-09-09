__author__ = 'Liam Childs'

if __name__ == '__main__' and __package__ is None:
    import lhc.io
    __package__ = 'lhc.io'

import argparse

from .gff_.iterator import GffEntryIterator
from .txt_.tools import compress, sort, index


def iter_gff(fname):
    return GffEntryIterator(fname)


# CLI


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()
    # Compress parser
    compress_parser = subparsers.add_parser('compress')
    compress.define_parser(compress_parser)
    compress_parser.set_defaults(block_delimiter='\n')
    # Sort parser
    sort_parser = subparsers.add_parser('sort')
    sort.define_parser(sort_parser)
    sort_parser.set_defaults(format='s1.i4.i5')
    # Index parser
    index_parser = subparsers.add_parser('index')
    index.define_parser(index_parser)
    index_parser.set_defaults(format='s1.r[i4.i5]')
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
