import argparse

from lhc.io.txt_.tools import check_format, compress, index, sort


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

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
