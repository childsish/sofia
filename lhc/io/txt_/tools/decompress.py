__author__ = 'Liam Childs'

import argparse
import gzip


def decompress(input, output):
    for line in input:
        output.write(line)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('input', nargs='?')
    parser.add_argument('output', nargs='?')
    parser.set_defaults(func=init_decompress)
    return parser


def init_decompress(args):
    import sys
    input = gzip.open(fileobj=sys.stdin) if args.input is None else gzip.open(args.input)
    output = sys.stdout if args.output is None else open(args.output)
    decompress(input, output)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
