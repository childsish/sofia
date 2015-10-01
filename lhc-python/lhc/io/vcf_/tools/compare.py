import argparse

from ..iterator import VcfLineIterator
from lhc.io.txt_ import Filter


def compare(a, b, filter=None):
    it_a = VcfLineIterator(a)
    it_b = VcfLineIterator(b)
    if filter is not None:
        it_a = Filter(it_a, filter, {'NOCALL': 'NOCALL', 'PASS': 'PASS'})
        it_b = Filter(it_b, filter, {'NOCALL': 'NOCALL', 'PASS': 'PASS'})
    set_a = set((line.chr, line.pos, line.ref, line.alt) for line in it_a)
    set_b = set((line.chr, line.pos, line.ref, line.alt) for line in it_b)
    sys.stdout.write('{}\t{}\t{}'.format(len(set_a - set_b), len(set_b - set_a), len(set_a & set_b)))


def main():
    args = get_parser().parse_args()
    args.func(args)

    
def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('a')
    add_arg('b')
    add_arg('-f', '--filter',
            help='filter for variants (default: none).')
    parser.set_defaults(func=init_compare)
    return parser


def init_compare(args):
    a = open(args.a)
    b = open(args.b)
    compare(a, b, args.filter)
    a.close()
    b.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
