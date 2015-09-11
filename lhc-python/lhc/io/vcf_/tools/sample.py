import argparse

from lhc.argparse import OpenWritableFile, OpenReadableFile


def sample(args):
    pass


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--bed')
    add_arg = parser.add_argument
    add_arg('-i', '--input', default=sys.stdin, action=OpenReadableFile)
    add_arg('-o', '--output', default=sys.stdout, action=OpenWritableFile)
    add_arg('number', type=int)
    add_arg('-r', '--randomise', action='store_true')
    add_arg('-s', '--seed', type=int)
    parser.set_defaults(func=sample_init)
    return parser


def sample_init(args):
    sample(args.input)

if __name__ == '__main__':
    import sys
    sys.exit(main())
