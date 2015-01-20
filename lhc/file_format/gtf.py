import argparse

from gtf_ import index
from gtf_.iterator import GtfEntityIterator


def iter_gtf(fname):
    return GtfEntityIterator(fname)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    index_parser = subparsers.add_parser('index')
    index.define_parser(index_parser)

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
