import argparse

from ..compressor import Compressor


def compress(input, output, block_size=65536, block_delimiter=None):
    compressor = Compressor(block_size, block_delimiter)
    compressor.compress(input, output)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?',
            help='input file name (default: stdin)')
    add_arg('output', nargs='?',
            help='output file name (default: stdout)')
    add_arg('-e', '--new-entry', default='\n',
            help='how to end blocks')
    parser.set_defaults(func=input)
    return parser


def init(args):
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    compress(input, output)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
