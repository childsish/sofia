import cPickle
import os

from argparse import ArgumentParser
from collections import namedtuple
from itertools import izip
from lhc.binf.genomic_coordinate import Position
from lhc.file_format.entry_set import EntrySet
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.fasta import FastaIndex

FastaEntry = namedtuple('FastaEntry', ('hdr', 'seq'))

class FastaParser(EntrySet):
    def __init__(self, fname, iname=None):
        super(FastaParser, self).__init__(fname, iname)
        self.index = None
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.index is None:
                infile = open(self.iname)
                self.index = cPickle.load(infile)
                infile.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.data = dict(iter(self))
        
        if isinstance(key, basestring):
            return self.data[key]
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.data[key.chr][key.pos]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.data[key.chr][key.start:key.stop]
        raise NotImplementedError('Random access not implemented for %s'%type(key))
    
    def _iterHandle(self, infile):
        hdr = None
        seq = None
        for line in infile:
            if line.startswith('>'):
                if hdr is not None:
                    yield FastaEntry(hdr, ''.join(seq))
                hdr = line.strip().split()[0][1:]
                seq = []
            else:
                seq.append(line.strip())
        yield FastaEntry(hdr, ''.join(seq))
    
    def _getIndexedData(self, key):
        if isinstance(key, basestring):
            res = IndexedFastaEntry(key, self.fname, self.index)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.index[key]
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in self.index.newlines:
                res = self.fhndl.read(1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self.index[Position(key.chr, key.start)]
            fpos_to = self.index[Position(key.chr, key.stop)]
            self.fhndl.seek(fpos_fr)
            res = ''.join(self.fhndl.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return res

class IndexedFastaEntry(object):
    def __init__(self, chr, fname, index):
        self.chr = chr
        self.fname = fname
        self.index = index
        self.fhndl = open(fname)
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            fpos = self.index[key]
            self.fhndl.seek(fpos)
            res = self.fhndl.read(1)
            while res in self.index.newlines:
                res = self.fhndl.read(1)
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self.index[Position(self.chr, key.start)]
            fpos_to = self.index[Position(self.chr, key.stop)]
            self.fhndl.seek(fpos_fr)
            res = ''.join(self.fhndl.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return res
    
    def __iter__(self):
        self.fhndl.seek(self.index)
        for line in self.fhndl:
            if line[0] == '>':
                break
            for char in line.strip():
                yield char

def iterEntries(fname):
    parser = FastaParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = FastaParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    cPickle.dump(_createKeyIndex(fname), outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createKeyIndex(fname):
    index = FastaIndex(fname)
    infile = open(fname, 'rb')
    fpos = 0
    for line in infile:
        if line.startswith('>'):
            hdr = line.strip().split()[0][1:]
            index[hdr] = fpos
        fpos += len(line)
    return index

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