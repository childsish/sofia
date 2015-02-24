import argparse
import pysam


def subset(args):
    if args.bed is not None:
        subset_bed(args.input, args.output, args.bed)
    elif args.random is not None:
        subset_random(args.input, args.output, args.random)


def subset_bed(input, output, bed):
    from lhc.io.bed import iter_entries as iter_bed
    visited = set()
    in_fhndl = pysam.AlignmentFile(input)
    out_fhndl = pysam.AlignmentFile(output, 'wb', template=in_fhndl)
    for entry in iter_bed(bed):
        for read in in_fhndl.fetch(entry.chr, entry.start, entry.stop):
            key = (read.query_name, read.flag)
            if key not in visited:
                visited.add(key)
                out_fhndl.write(read)
    in_fhndl.close()
    out_fhndl.close()


def subset_random(input, output, proportion):
    raise NotImplementedError()
    in_fhndl = pysam.AlignmentFile(input)
    out_fhndl = pysam.AlignedFile(output, 'wb', template=in_fhndl)
    in_fhndl.close()
    out_fhndl.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bed',
                       help='Get reads that overlap with the ranges defined in a bed file.')
    group.add_argument('-r', '--random', type=float, default=0.1,
                       help='Sample the given proportion of reads from the input.')

    add_arg = parser.add_argument
    add_arg('input', default='-',
            help='The input bam file.')
    add_arg('-o', '--output', default='-',
            help='The output bam file.')
    parser.set_defaults(func=subset)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
