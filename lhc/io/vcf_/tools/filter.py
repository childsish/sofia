import argparse

from ..iterator import VcfLineIterator
from lhc.io.txt_ import Filter


def filter(input, output, filters):
    it = VcfLineIterator(input)
    filtered_it = Filter(it, filters, {'NOCALL': 'NOCALL', 'PASS': 'PASS'})
    for k, vs in it.hdrs.iteritems():
        output.write('\n'.join('{}={}'.format(k, v) for v in vs))
    output.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(it.samples) + '\n')
    for line in filtered_it:
        output.write(line)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', nargs='?',
            help='The name of the vcf_ file to be filtered (default: stdin).')
    add_arg('output', nargs='?',
            help='The name of the filtered vcf_ file (default: stdout).')
    add_arg('-f', '--filter', nargs='+', default=[],
            help='Filters to apply (default: none).')
    parser.set_defaults(func=filter_init)
    return parser


def filter_init(args):
    import sys
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    filter(input, output, args.filters)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
