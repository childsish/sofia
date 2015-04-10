import os

from sofia_.step import Resource, Target
from lhc.io.bed_.index import IndexedBedFile
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet as BedSetBase
from warnings import warn


class BedIterator(Target):
    
    EXT = {'.bed', '.bed.gz'}
    FORMAT = 'bed'
    OUT = ['genomic_interval']
    
    def init(self):
        self.parser = BedLineIterator(self.get_filename())

    def calculate(self):
        return self.parser.next()

    def format(self, genomic_interval):
        return genomic_interval['data'].name


class BedSet(Resource):
    
    EXT = {'.bed', '.bed.gz', '.bed.bgz'}
    FORMAT = 'bed'
    OUT = ['genomic_interval_set']

    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedBedFile(pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedBedFile(index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = BedSetBase(BedLineIterator(fname))
