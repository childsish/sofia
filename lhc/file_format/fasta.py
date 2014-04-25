import cPickle
import gzip
import os

from argparse import ArgumentParser
from collections import namedtuple
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
            res = FastaEntry(key, self.fhndl, self.index)
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

class FastaEntry(object):
    def __init__(self, chr, fhndl, index):
        self.chr = chr
        self.fhndl = fhndl
        self.index = index
    
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
    infile = gzip.open(fname, 'rb') if fname.endswith('.gz') else\
        open(fname, 'rb')
    while True:
        line = infile.readline()
        fpos = infile.tell()
        if line == '':
            break
        elif line.startswith('>'):
            hdr = line.split()[0][1:]
            print hdr
            index[hdr] = fpos
    return index

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = ArgumentParser()
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
