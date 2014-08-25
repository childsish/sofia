from csv import iterCsv, ColumnBuilder, FieldBuilder
from lhc.binf.genomic_coordinate import Interval

from bed_.iterator import BedIterator
from bed_.index import BedFileIndexer

def iterEntries(fname):
    """ Convenience function """
    return BedIterator(fname)

def index(fname, iname=None):
    if fname.endswith('.gz'):
        raise IOError('Unable to index compressed files.')
    
    indexed = BedFileIndexer()
    ivl_index = indexer.index(fname)
    
    iname = '%s.idx'%fname if iname in None else iname
    fhndl = open(iname, 'wb')
    cPickle.dump(fname, fhndl, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, fhndl, cPickle.HIGHEST_PROTOCOL)
    fhndl.close()

