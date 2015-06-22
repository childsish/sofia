import argparse

from .gtf_.iterator import GtfEntryIterator
from .txt_.tools import compress, sort


def iter_gtf(fname):
    return GtfEntryIterator(fname)


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
    sort_parser.set_defaults(format=('s1', 'i4'))
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
