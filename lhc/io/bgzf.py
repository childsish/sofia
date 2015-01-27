import argparse

from Bio.bgzf import BgzfWriter
from lhc.filetools.flexible_opener import open_flexibly


def compress(args):
    fname, fhndl = open_flexibly(args.input)
    if fname == 'stdin':
        raise ValueError('stdin disabled')
    writer = BgzfWriter('{}.bgz'.format(args.input))
    while True:
        data = fhndl.read(65536)
        writer.write(data)
        if not data:
            break
    fhndl.close()
    writer.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input')
    parser.set_defaults(func=compress)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
