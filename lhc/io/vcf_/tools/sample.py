import argparse
import random

from ..iterator import VcfLineIterator


def sample(input, output, proportion):
    it = VcfLineIterator(input)
    for k, vs in it.hdrs.iteritems():
        output.write('\n'.join('{}={}'.format(k, v) for v in vs))
    output.write('\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(it.samples) + '\n')
    for line in it:
        if random.random() < proportion:
            output.write('{}\n'.format(line))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?')
    add_arg('output', nargs='?')
    add_arg('-p', '--proportion', default=0.01, type=float)
    add_arg('-s', '--seed', type=int)
    parser.set_defaults(func=sample_init)
    return parser


def sample_init(args):
    import sys
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    if args.seed is not None:
        random.seed(args.seed)
    sample(input, output, args.proportion)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
