import argparse

from gtf_.iterator import GtfEntryIterator
from lhc.io.txt_ import compress


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
    compress_parser = compress.define_parser(compress_parser)
    compress_parser.set_defaults(column_types=['1s', '4,5v'])

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
