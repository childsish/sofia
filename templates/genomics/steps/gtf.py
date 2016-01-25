import os

from sofia_.step import Resource, Target
from lhc.io.gtf_.index import IndexedGtfFile
from lhc.io.gtf_.iterator import GtfEntryIterator
from lhc.io.gtf_.set_ import GtfSet as GtfSetBase
from warnings import warn


class GtfIterator(Target):
    
    EXT = {'.gtf', '.gtf.gz', '.gtf.bgz'}
    FORMAT = 'gtf_file'
    OUT = ['genomic_feature']

    def get_interface(self, filename):
        return GtfEntryIterator(filename)

    def calculate(self):
        try: #REMOVEME
            entry = self.interface.next()
        except Exception:
            return None
        while entry.type != 'gene':
            entry = self.interface.next()
        entry.name = entry.name.rsplit('.')[0]
        return entry


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz', '.gtf.bgz']
    FORMAT = 'gtf_file'
    OUT = ['genomic_feature_set']

    def get_interface(self, filename):
        if os.path.exists('{}.tbi'.format(filename)):
            try:
                import pysam
                return IndexedGtfFile(pysam.TabixFile(filename))
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(filename)):
            from lhc.io.txt_ import index
            return IndexedGtfFile(index.IndexedFile(filename))
        warn('no index available for {}, loading whole file...'.format(filename))
        return GtfSetBase(GtfEntryIterator(filename))
