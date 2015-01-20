import argparse
import bz2


class Indexer(object):
    """
    Indexes bz2 files
    """

    def index(self, fname, key):
        res = {}
        return res


def index(args):
    pass


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.set_defaults(func=index)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
