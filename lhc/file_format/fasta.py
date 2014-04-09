import cPickle
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
        self.fname = fname
        self.iname = self.getIndexName(fname) if iname is None else iname
        self.key_index = None
        self.seq_index = None
        self.data = None
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.key_index is None:
                infile = open(self.iname)
                self.key_index = cPickle.load(infile)
                self.seq_index = cPickle.load(infile)
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
        infile = open(self.fname)
        if isinstance(key, basestring):
            fpos = self.key_index[key]
            infile.seek(fpos)
            infile.readline()
            seq = []
            for line in infile:
                if line.startswith('>'):
                    break
                seq.append(line.strip())
            res = ''.join(seq)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.seq_index[key]
            infile.seek(fpos)
            res = infile.read(1)
            while res in self.seq_index.newlines:
                res = infile.read(1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fpos_fr = self.seq_index[Position(key.chr, key.start)]
            fpos_to = self.seq_index[Position(key.chr, key.stop)]
            infile.seek(fpos_fr)
            res = ''.join(infile.read(fpos_to - fpos_fr).split())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        infile.close()
        return res

def iterEntries(fname):
    parser = FastaParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = FastaParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    cPickle.dump(_createKeyIndex(fname), outfile)
    cPickle.dump(_createSeqIndex(fname), outfile)
    outfile.close()

def _createKeyIndex(fname):
    index = ExactKeyIndex()
    infile = open(fname, 'rb')
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.startswith('>'):
            index[line.split()[0][1:]] = fpos
    infile.close()
    return index

def _createSeqIndex(fname):
    index = FastaIndex(fname)
    infile = open(fname, 'rb')
    while True:
        line = infile.readline()
        fpos = infile.tell()
        if line == '':
            break
        elif line.startswith('>'):
            hdr = line.split()[0][1:]
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
