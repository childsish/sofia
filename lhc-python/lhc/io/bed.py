import argparse

from bed_ import depth
from bed_.iterator import BedEntryIterator


def iter_bed(fname):
    it = BedEntryIterator(fname)
    for entry in it:
        yield entry
    it.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    depth_parser = subparsers.add_parser('depth')
    depth.define_parser(depth_parser)

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
