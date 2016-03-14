import argparse


def inspect(handle):
    raise NotImplementedError('removed until bgzf can be re-implemented')
    data_start = 0
    i = 0
    while True:
        #block_length, data = _load_bgzf_block(handle)
        data_len = len(data)
        print 'block {}'.format(i)
        print repr(data[:data.find('\n') + 1])
        print repr(data[data.rfind('\n', 0, len(data) - 1) + 1:])
        data_start += data_len
        i += 1


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?',
            help='input file name (default: stdin)')
    parser.set_defaults(func=init_inspect)
    return parser


def init_inspect(args):
    import sys
    input = sys.stdin if args.input is None else open(args.input, 'rb')
    inspect(input)
    input.close()
