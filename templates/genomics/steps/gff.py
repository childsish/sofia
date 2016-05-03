import gzip
import os

from sofia_.step import Resource, Target
from lhc.io.gff_.index import IndexedGffFile
from lhc.io.gff_.iterator import GffEntryIterator
from lhc.io.gff_.set_ import GffSet as GffSetBase
from warnings import warn


class GffIterator(Target):
    
    EXT = {'.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz'}
    FORMAT = 'gff_file'
    OUT = ['genomic_feature']

    def get_interface(self, filename):
        return iter(GffEntryIterator(filename))

    def calculate(self):
        entry = self.interface.next()
        while entry.type != 'gene':
            entry = self.interface.next()
        entry.name = entry.name.rsplit('.')[0]
        return entry


class GffSet(Resource):
    
    EXT = ['.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz']
    FORMAT = 'gff_file'
    OUT = ['genomic_feature_set']

    def get_interface(self, filename):
        if os.path.exists('{}.tbi'.format(filename)):
            try:
                import pysam
                return IndexedGffFile(pysam.TabixFile(filename))
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(filename)):
            from lhc.io.txt_ import index
            return IndexedGffFile(index.IndexedFile(filename))
        warn('no index available for {}, loading whole file...'.format(filename))
        fileobj = gzip.open(filename) if filename.endswith('.gz') else\
            open(filename)
        return GffSetBase(GffEntryIterator(fileobj))
