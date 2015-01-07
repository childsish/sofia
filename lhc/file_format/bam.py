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
    parser = get_parser()
    args = parser.parse_args()
    if args.sample:
        rename_sample(args)

def get_parser():
    parser = argparse.ArgumentParser()
    return define_parser(parser)

def define_parser(parser):
    parser.add_argument('input')
    parser.add_argument('-o', '--output', default='-',
        help='The output destination (default: stdout)')
    parser.add_argument('-s', '--sample',
        help='Rename sample')
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
