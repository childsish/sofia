import argparse

from bgzf_.tools import inspect


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    inspect_parser = subparsers.add_parser('inspect')
    inspect.define_parser(inspect_parser)

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
