__author__ = 'Liam Childs'

if __name__ == '__main__' and __package__ is None:
    import lhc.io
    __package__ = 'lhc.io'

import argparse

from .txt_.tools import check_format, compress, index, sort, fetch


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    check_format_parser = subparsers.add_parser('check_format')
    check_format.define_parser(check_format_parser)

    compress_parser = subparsers.add_parser('compress')
    compress.define_parser(compress_parser)

    index_parser = subparsers.add_parser('index')
    index.define_parser(index_parser)

    sort_parser = subparsers.add_parser('sort')
    sort.define_parser(sort_parser)

    fetch_parser = subparsers.add_parser('fetch')
    fetch.define_parser(fetch_parser)

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
