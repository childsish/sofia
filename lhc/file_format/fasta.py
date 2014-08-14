import cPickle
import os

from argparse import ArgumentParser
from collections import namedtuple
from itertools import izip
from lhc.indices.fasta import FastaIndex
from lhc.file_format.fasta_.index import FastaFileIndexer

FastaEntry = namedtuple('FastaEntry', ('hdr', 'seq'))

def iterEntries(fname):
    parser = FastaParser(fname)
    return iter(parser)

def index(fname, iname=None):
    indexer = FastaFileIndexer()
    index = indexer.index(fname)
    
    iname = '%s.idx'%fname if iname is None else iname
    fhndl = open(iname, 'wb')
    cPickle.dump(fname, fhndl, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(index, fhndl, cPickle.HIGHEST_PROTOCOL)
    fhndl.close()
    
def compare(a_fname, b_fname):
    a_index = _createKeyIndex(a_fname)
    b_index = _createKeyIndex(b_fname)
    a_chrs = set(a_index.chrs)
    b_chrs = set(b_index.chrs)
    
    a_only = sorted(a_chrs - b_chrs)
    print '%d headers unique to first fasta:'%len(a_only)
    print '\n'.join(a_only)
    b_only = sorted(b_chrs - a_chrs)
    print '%d headers unique to second fasta:'%len(b_only)
    print '\n'.join(b_only)
    both = sorted(a_chrs & b_chrs)
    print '%d headers common to both fastas:'%len(both)
    print '\n'.join(both)
    
    print 'The common headers differ at the following positions:'
    a_parser = FastaParser(a_fname)
    b_parser = FastaParser(b_fname)
    for hdr in both:
        for i, (a, b) in enumerate(izip(a_parser[hdr], b_parser[hdr])):
            if a.lower() != b.lower():
                print '%s starts to differ at position %d: %s %s'%(hdr, i, a, b)
                break

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    
    compare_parser = subparsers.add_parser('compare')
    compare_parser.add_argument('input_a')
    compare_parser.add_argument('input_b')
    compare_parser.set_defaults(func=lambda args: compare(args.input_a, args.input_b))
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())

