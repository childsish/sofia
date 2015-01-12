import argparse

from iterator import VcfLineIterator
from lhc.argparse import OpenReadableFile, OpenWritableFile


def filter(args):
    it = VcfLineIterator(args.input)
    fhndl = sys.stdout if args.output is None else open(args.output, 'w')
    for k, vs in it.hdrs.iteritems():
        for v in vs:
            fhndl.write('{}={}\n'.format(k, v))
    fhndl.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(it.samples) + '\n')
    for line in it:
        if float(line.qual) < args.quality:
            continue
        fhndl.write(line)
    fhndl.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('-i', '--input', default=sys.stdin, action=OpenReadableFile,
            help='The name of the vcf file to be filtered.')
    add_arg('-o', '--output', default=sys.stdout, action=OpenWritableFile,
            help='The name of the filtered vcf file.')
    add_arg('-q', '--quality', type=float, default=0,
            help='Variants below the given quality will be filtered (default: 0).')
    parser.set_defaults(func=filter)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
