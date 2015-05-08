import cPickle
import os

from collections import namedtuple
from lhc.io.entry_set import EntrySet
from lhc.indices.key_index import KeyIndex

Association = namedtuple('Association', ('chr', 'pos', 'ref', 'alt', 'n', 'f', 'beta', 'se', 'stat', 'p'))

def iterEntries(fname):
    parser = PseqParser(fname)
    return iter(parser)

class PseqParser(EntrySet):

    POS = 0
    REF = 1
    ALT = 2
    N = 3
    F = 4
    BETA = 5
    SE = 6
    STAT = 7
    P = 8
    
    def __init__(self, fname, iname=None):
        super(PseqParser, self).__init__(fname, iname)
        self.pos_index = None
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.pos_index is None:
                infile = open(self.iname)
                self.pos_index = cPickle.load(infile)
                infile.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.pos_index = KeyIndex()
            self.data = list(iter(self))
            for i, entry in enumerate(self.data):
                self.pos_index[(entry.chr, entry.pos)] = i
        
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.data[self.pos_index[(key.chr, key.pos)]]
        raise NotImplementedError('Random access not implemented for %s'%type(key))
    
    def _iterHandle(self, infile):
        infile.next()
        for line in infile:
            parts = line.strip().split('\t')
            chr, pos = parts[self.POS].split(':')
            if '..' in pos:
                pos = pos.split('..')[0]
            yield Association(chr,
                int(pos) - 1,
                parts[self.REF],
                parts[self.ALT],
                int(parts[self.N]),
                float(parts[self.F]),
                float(parts[self.BETA]),
                'NA' if parts[self.SE] == 'NA' else float(parts[self.SE]),
                'NA' if parts[self.STAT] == 'NA' else float(parts[self.STAT]),
                'NA' if parts[self.P] == 'NA' else float(parts[self.P]))

    def _getIndexedData(self, key):
        res = []
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.pos_index[(key.chr, key.pos)][0]
            self.fhndl.seek(fpos.value)
            res = self._iterHandle(self.fhndl, self.hdrs).next()
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return res
    
def index(fname, iname=None):
    iname = PseqParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    pos_index = _createIndices(fname)
    cPickle.dump(pos_index, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createIndices(fname):
    pos_index = KeyIndex()
    infile = open(fname, 'rb')
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.strip() == '' or line.startswith('#'):
            continue
        entry = PseqParser._parseUnsampledLine(line)
        pos_index[(entry.chr, entry.pos)] = fpos
    infile.close()
    return pos_index, ivl_index

