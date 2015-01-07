from argparse import ArgumentParser
from itertools import izip
from fasta_.index import IndexedFastaFile
from fasta_.iterator import FastaEntryIterator
from fasta_.set_ import FastaSet


def iter_entries(fname):
    """ Convenience function """
    return FastaEntryIterator(fname)


def compare(a_fname, b_fname):
    a_hdrs = _get_headers(a_fname)
    b_hdrs = _get_headers(b_fname)

    a_only = sorted(a_hdrs - b_hdrs)
    print '{} headers unique to first fasta:'.format(len(a_only))
    print '\n'.join(a_only)
    b_only = sorted(b_hdrs - a_hdrs)
    print '{} headers unique to second fasta:'.format(len(b_only))
    print '\n'.join(b_only)
    both = sorted(a_hdrs & b_hdrs)
    print '{} headers common to both fastas:'.format(len(both))
    print '\n'.join(both)

    print 'The common headers differ at the following positions:'
    a_parser = FastaEntryIterator(a_fname)
    b_parser = FastaEntryIterator(b_fname)
    for hdr in both:
        for i, (a, b) in enumerate(izip(a_parser[hdr], b_parser[hdr])):
            if a.lower() != b.lower():
                print '{} starts to differ at position {}: {} {}'.format(hdr, i, a, b)
                break


def _get_headers(fname):
    fhndl = open(fname)
    hdrs = [line for line in fhndl if line.startswith('>')]
    fhndl.close()
    return hdrs


def extract(fname, header, out_fname=None):
    out_fhndl = sys.stdout if out_fname is None else open(out_fname, 'w')
    fhndl = open(fname)
    extracting = False
    for line in fhndl:
        if line[0] == '>':
            if extracting:
                break
            elif line[1:].startswith(header):
                extracting = True
        if extracting:
            out_fhndl.write(line)
    fhndl.close()
    out_fhndl.close()


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    compare_parser = subparsers.add_parser('compare')
    compare_parser.add_argument('input_a')
    compare_parser.add_argument('input_b')
    compare_parser.set_defaults(func=lambda args: compare(args.input_a, args.input_b))

    extract_parser = subparsers.add_parser('extract')
    extract_parser.add_argument('input')
    extract_parser.add_argument('header')
    extract_parser.add_argument('-o', '--output')
    extract_parser.set_defaults(func=lambda args: extract(args.input, args.header, args.output))

    return parser


if __name__ == '__main__':
    import sys

    sys.exit(main())
