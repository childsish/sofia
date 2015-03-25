import os

from sofia_.step import Resource, Target
from lhc.io.gff_.index import IndexedGffFile
from lhc.io.gff_.iterator import GffEntryIterator
from lhc.io.gff_.set_ import GffSet as GffSetBase
from warnings import warn


class GffIterator(Target):
    
    EXT = ['.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz']
    OUT = ['genomic_feature']

    def init(self):
        self.parser = iter(GffEntryIterator(self.get_filename()))

    def calculate(self):
        entry = self.parser.next()
        while entry.type != 'gene':
            entry = self.parser.next()
        entry.name = entry.name.rsplit('.')[0]
        return entry


class GffSet(Resource):
    
    EXT = ['.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz']
    OUT = ['genomic_feature_set']

    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedGffFile(pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedGffFile(index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = GffSetBase(GffEntryIterator(fname))
