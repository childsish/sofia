import argparse

from bam_ import rename, subset


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    rename_parser = subparsers.add_parser('rename')
    rename.define_parser(rename_parser)

    subset_parser = subparsers.add_parser('subset')
    subset.define_parser(subset_parser)

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
