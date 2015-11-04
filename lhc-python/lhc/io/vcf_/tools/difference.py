__author__ = 'Liam Childs'

import argparse
import gzip
import pysam

from ..iterator import VcfLineIterator


def difference(left_iterator, right_set):
    exc, inc = 0, 0
    for k, vs in left_iterator.hdrs.iteritems():
        for v in vs:
            yield '{}={}\n'.format(k, v)
    yield '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(left_iterator.samples) + '\n'
    for left in left_iterator:
        try:
            rights = (VcfLineIterator.parse_line(right) for right in right_set.fetch(left.chr, left.pos))
        except ValueError:
            rights = []
        if (left.chr, left.pos) in {(right.chr, right.pos) for right in rights}:
            exc += 1
            continue
        inc += 1
        yield '{}\n'.format(left)
    import sys
    sys.stderr.write('{} variants were kept and {} removed\n'.format(inc, exc))


def main():
    args = get_parser().parse_args()
    args.func(args)

    
def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('left', nargs='?',
                        help='left side (default: stdin)')
    parser.add_argument('right',
                        help='right side')
    parser.add_argument('output', nargs='?',
                        help='output file (default: stdout)')
    parser.set_defaults(func=init_difference)
    return parser


def init_difference(args):
    import sys
    left = sys.stdin if args.left is None else\
           gzip.open(args.left) if args.left.endswith('.gz') else\
           open(args.left)
    left = VcfLineIterator(left)
    right = pysam.TabixFile(args.right)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    for line in difference(left, right):
        output.write(line)
    left.close()
    right.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())

