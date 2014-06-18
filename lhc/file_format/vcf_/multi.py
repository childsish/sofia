import cPickle
import os

from parser import VcfParser
from itertools import izip, chain
from lhc.binf.genomic_coordinate import Interval
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.filepool import FilePool

class MultiVcfParser(VcfParser):
    
    def __init__(self, fnames, iname=None):
        super(VcfParser, self).__init__(fnames, iname)
        self.pos_index = None
        self.ivl_index = None
        self.filepool = FilePool()
        self.hdrs = [self._parseHeaders(self.filepool[fname]) for fname in fnames]
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.pos_index is None:
                fhndl = open(self.iname)
                self.pos_index = cPickle.load(fhndl)
                self.ivl_index = cPickle.load(fhndl)
                fhndl.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.pos_index = Index((ExactKeyIndex, ExactKeyIndex))
            self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
            self.data = [self._iterHandle(self.filepool[fname], hdr) for fname, hdr in izip(self.fname, self.hdrs)]
            for i, data in enumerate(self.data):
                for j, entry in enumerate(data):
                    ivl = Interval(entry.chr, entry.pos, entry.pos + len(entry.ref))
                    if (entry.chr, entry.pos) not in self.pos_index:
                        self.pos_index[(entry.chr, entry.pos)] = []
                    self.pos_index[(entry.chr, entry.pos)].append((i, j))
                    if (entry.chr, ivl) not in self.ivl_index:
                        self.ivl_index[(entry.chr, ivl)] = []
                    self.ivl_index[(entry.chr, ivl)].append((i, j))
        
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            indices = self.pos_index[(key.chr, key.pos)].value
            return [self.data[i][j] for i, j in indices]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            indices = chain(index.value for index in self.ivl_index[(key.chr, key)])
            return [self.data[i][j] for i, j in indices]
        raise NotImplementedError('Random access not implemented for %s'%type(key))
