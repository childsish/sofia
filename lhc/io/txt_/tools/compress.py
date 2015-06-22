import argparse

from Bio.bgzf import BgzfWriter


def compress(input, output):
    if not isinstance(output, BgzfWriter):
        output = BgzfWriter(fileobj=output)
    data = ''
    while True:
        data += input.read(65536 - len(data))
        if not data:
            break
        idx = data.rfind('\n')
        output.write(data[:idx])
        output.flush()
        data = data[idx:]


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
