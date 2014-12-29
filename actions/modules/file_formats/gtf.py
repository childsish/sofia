import argparse
import gzip

from gtf_.index import IndexedGtfFile
from gtf_.set_ import GtfSet
from gtf_.iterator import GtfIterator


def iter_entries(fname):
    """ Convenience function """
    return GtfIterator(fname)


def index(fname):
    """ Query a gtf file by model name. Use tabix for interval queries. """
    index = []
    fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
    for line in fhndl:
        if line.startswith('#'):
            continue
        type, ivl, attr = GtfIterator._parse_line(line)
        if type == 'gene':
            index.append('%s\t%s\t%d\t%d' % (attr['gene_name'], ivl.chr, ivl.start + 1, ivl.stop + 1))
    fhndl.close()

    iname = '%s.lhci' % fname
    fhndl = open(iname, 'w')
    fhndl.write('\n'.join(index))
    fhndl.close()


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('input')
    index_parser.set_defaults(func=lambda args: index(args.input))

    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())

