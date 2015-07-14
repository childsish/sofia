__author__ = 'Liam Childs'

import argparse
import os


def split(input, output):
    outfile = None
    for line in input:
        if line.startswith('LOCUS'):
            if outfile is not None:
                outfile.close()
            outfname = '%{}.gbk'.format(line.split()[1])
            outfile = open(os.path.join(output, outfname), 'w')
        outfile.write(line)
    outfile.close()
    input.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument

    add_arg('input')
    add_arg('output',
            help='directory for split output')

    parser.set_defaults(func=init_split)
    return parser


def init_split(args):
    split(args.input, args.output)


if __name__ == '__main__':
    import sys
    sys.exit(main())
