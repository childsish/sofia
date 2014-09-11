import argparse
import cPickle
import os

from lhc.file_format.gtf_.iterator import GtfIterator
from lhc.file_format.gtf_.index import GtfFileIndexer

def iterEntries(fname):
    """ Convenience function """
    return GtfIterator(fname)

def index(fname, iname=None):
    if fname.endswith('.gz'):
        raise IOError('Unable to index compressed files.')
    
    indexer = GtfFileIndexer()
    key_index, ivl_index = indexer.index(fname)
    
    iname = '%s.idx'%fname if iname is None else iname
    fhndl = open(iname, 'wb')
    cPickle.dump(os.path.abspath(fname), fhndl, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(key_index, fhndl, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, fhndl, cPickle.HIGHEST_PROTOCOL)
    fhndl.close()

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('input', metavar='FILE')
    index_parser.add_argument('-o', '--output', metavar='FILE')
    index_parser.set_defaults(func=lambda args:index(args.input))

    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
