import argparse

from Bio.bgzf import BgzfWriter


def compress(input, output, block_size=65536, block_delimiter='\n'):
    data = ''
    while True:
        data += input.read(block_size - len(data))
        if not data:
            break
        idx = data.rfind(block_delimiter, 0, block_size)
        output.write(data[:idx + 1])
        output.flush()
        data = data[idx + 1:]


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
    add_arg('-d', '--block-delimiter', default='\n',
            help='block can only end with this string. Set to "" for no delimiter')
    add_arg('-s', '--block-size', default=65536,
            help='maximum uncompressed size of a block (default: 65536)')
    parser.set_defaults(func=init_compress)
    return parser


def init_compress(args):
    import sys
    input = sys.stdin if args.input is None else open(args.input)
    output = BgzfWriter(fileobj=sys.stdout) if args.output is None else BgzfWriter(args.output, 'wb')
    compress(input, output, args.block_size, args.block_delimiter)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
