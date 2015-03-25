import os

from sofia_.step import Resource, Target
from lhc.io.gtf_.index import IndexedGtfFile
from lhc.io.gtf_.iterator import GtfEntryIterator
from lhc.io.gtf_.set_ import GtfSet as GtfSetBase
from warnings import warn


class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz', '.gtf.bgz']
    OUT = ['genomic_feature']

    def init(self):
        self.parser = GtfIterator(self.get_filename())

    def calculate(self):
        entry = self.parser.next()
        while entry.type != 'gene':
            entry = self.parser.next()
        entry.name = entry.name.rsplit('.')[0]
        return entry


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz', '.gtf.bgz']
    OUT = ['genomic_feature_set']

    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedGtfFile(pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedGtfFile(index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = GtfSetBase(GtfEntryIterator(fname))
