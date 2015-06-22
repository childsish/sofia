import argparse

from .gtf_.iterator import GtfEntryIterator
from .txt_.tools import compress


def iter_gtf(fname):
    return GtfEntryIterator(fname)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()
    compress_parser = subparsers.add_parser('compress')
    compress.define_parser(compress_parser)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
