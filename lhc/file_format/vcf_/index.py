from lhc.indices.index import Index
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.indices.exact_key import ExactKeyIndex

class VcfFileIndexer(object):
    def index(self, fname):
        ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
        infile = open(fname, 'rb')
        while True:
            fpos = infile.tell()
            line = infile.readline()
            if line == '':
                break
            elif line.strip() == '' or line.startswith('#'):
                continue
            entry = VcfParser._parseUnsampledLine(line)
            ivl = Interval(entry.pos, entry.pos + len(entry.ref))
            ivl_index[(entry.chr, ivl)] = fpos
        infile.close()
        return ivl_index

class IndexedVcfFile(object):
    def __init__(self, iname):
        self.iname = iname
        fhndl = open(iname)
        self.fname = cPickle.load(fhndl)
        self.ivl_index = cPickle.load(fhndl)
        fhndl.close()
        self.iterator = VcfIterator(self.fname)

        self.prv_key = None
        self.prv_value = None
    
    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            ivl = Interval(key.pos, key.pos + len(key.ref))
            fposs = self.ivl_index[(key.chr, ivl)]
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            ivl = Interval(key.pos, key.pos + 1)
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

