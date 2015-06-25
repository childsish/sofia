import argparse

from ..iterator import VcfLineIterator

def compare(a, b, quality):
    a = set((line.chr, line.pos, line.ref, line.alt) for line in VcfLineIterator(a)
            if float(line.qual) > quality)
    b = set((line.chr, line.pos, line.ref, line.alt) for line in VcfLineIterator(b)
            if float(line.qual) > quality)

    print '{}\t{}\t{}'.format(len(a - b), len(b - a), len(a & b))


def main():
    args = get_parser().parse_args()

    
def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('a')
    add_arg('b')
    add_arg('-q', '--quality', default=0, type=float,
            help='Filter variants by quality before comparison (default: 0).')
    parser.set_defaults(func=init_compare)
    return parser

def init_compare(args):
    a = open(args.a)
    b = open(args.b)
    compare(a, b, args.quality)
    a.close()
    b.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
