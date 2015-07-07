#!/usr/bin/python

import argparse
import gzip
import sys

from ..merger import VcfMerger


def merge(fnames, out, bams, filters):
    merger = VcfMerger(fnames, bams=bams, filters=filters)
    for key, values in merger.hdrs.iteritems():
        for value in values:
            out.write('{}={}\n'.format(key, value))
    out.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(merger.samples) + '\n')
    for entry in merger:
        format = sorted(key for key in entry.samples.itervalues().next().keys() if key != '.')
        out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            entry.chr,
            entry.pos + 1,
            entry.id,
            entry.ref,
            entry.alt,
            entry.qual,
            entry.filter,
            entry.info,
            ':'.join(format),
            '\t'.join('.' if '.' in entry.samples[sample] else
                      ':'.join(entry.samples[sample][f] for f in format)
                      for sample in merger.samples)
        ))
    out.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    add_arg = parser.add_argument
    add_arg('inputs', nargs='+')
    add_arg('-b', '--bams', nargs='+',
            help='If provided, the read counts from the bam files with be included.')
    add_arg('-o', '--output',
            help='The name of the merged vcf_ (default: stdout).')
    add_arg('-f', '--filter', nargs='+', default=[],
            help='Filters to apply')
    parser.set_defaults(func=init_merge)
    return parser


def init_merge(args):
    inputs = [gzip.open(i) if i.endswith('gz') else open(i) for i in args.inputs]
    output = sys.stdout if args.output is None else open(args.output)
    merge(inputs, output, args.bams, args.filter)


if __name__ == '__main__':
    import sys
    sys.exit(main())
