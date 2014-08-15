import cPickle

from lhc.interval import Interval
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.file_format.gtf_.iterator import GtfIterator

class GtfFileIndexer(object):
    def index(self, fname):
        key_index = ExactKeyIndex()
        ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
        infile = open(fname, 'rb')
        fpos = 0
        for line in infile:
            if line.startswith('#') or line.strip() == '':
                fpos += len(line)
                continue
            type, ivl, attr = GtfIterator._parseLine(line)
            if type == 'gene':
                key_index[attr['gene_name']] = fpos
                ivl_index[(ivl.chr, Interval(ivl.start, ivl.stop))] = fpos
            fpos += len(line)
        infile.close()
        return key_index, ivl_index
    
class IndexedGtfFile(object):
    def __init__(self, iname):
        self.iname = iname
        fhndl = open(iname)
        self.fname = cPickle.load(fhndl)
        self.key_index = cPickle.load(fhndl)
        self.ivl_index = cPickle.load(fhndl)
        fhndl.close()
        self.iterator = GtfIterator(self.fname)
        
        self.prv_key = None
        self.prv_value = None
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            fposs = [self.key_index[key]]
        elif hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            ivl = Interval(key.pos, key.pos + len(key.ref))
            fposs = self.ivl_index[(key.chr, ivl)]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fposs = self.ivl_index[(key.chr, key)]
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        
        if self.prv_key != fposs:
            self.prv_key = fposs
            self.prv_value = [self._getEntryAtFilePosition(fpos) for fpos in fposs]
        return self.prv_value
    
    def _getEntryAtFilePosition(self, fpos):
        self.iterator.seek(fpos.value)
        return self.iterator.next()
