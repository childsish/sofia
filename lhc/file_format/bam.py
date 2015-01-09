import argparse

from bam_ import rename_sample


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    rename_parser = subparsers.add_parser('rename')
    rename_sample.define_parser(rename_parser)

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
