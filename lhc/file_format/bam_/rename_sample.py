import argparse
import pysam


def rename_sample(args):
    in_fhndl = pysam.AlignmentFile(args.input)
    header = in_fhndl.header.copy()
    header['RG'][0]['SM'] = args.sample
    out_fhndl = pysam.AlignmentFile(args.output, 'wb', header=header)
    for read in in_fhndl:
        out_fhndl.write(read)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('-i', '--input', default='-',
            help='The input file (default: stdin)')
    add_arg('-o', '--output', default='-',
            help='The output destination (default: stdout)')
    parser.set_defaults(func=rename_sample)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
