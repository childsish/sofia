import os

from sofia_.step import Resource, Target
from lhc.io.vcf_.tools.index import IndexedVcfFile
from lhc.io.vcf_.iterator import VcfEntryIterator
from lhc.io.vcf_.set_ import VcfSet as VcfSetBase
from lhc.io.vcf_.tools.split_alt import _split_variant
from warnings import warn


class VcfIterator(Target):
    
    EXT = {'.vcf', '.vcf.gz'}
    FORMAT = 'vcf'
    OUT = ['variant']
    
    def init(self):
        self.fileobj = open(self.get_filename())
        self.parser = iter(VcfEntryIterator(self.fileobj))
        self.variants = []

    def calculate(self):
        if len(self.variants) == 0:
            self.variants = _split_variant(self.parser.next())
        return self.variants.pop()


class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = {'.vcf', '.vcf.gz'}
    FORMAT = 'vcf'
    OUT = ['variant_set']
    
    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedVcfFile(fname, pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedVcfFile(fname, index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = VcfSetBase(VcfEntryIterator(fname))
