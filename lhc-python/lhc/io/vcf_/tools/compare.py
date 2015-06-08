import argparse

from ..iterator import VcfLineIterator

def compare(args):
    a = set((line.chr, line.pos, line.ref, line.alt) for line in VcfLineIterator(args.a)
            if float(line.qual) > args.quality)
    b = set((line.chr, line.pos, line.ref, line.alt) for line in VcfLineIterator(args.b)
            if float(line.qual) > args.quality)

    print len(a)
    print len(b)
    print len(a & b)


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
    parser.set_defaults(func=compare)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
