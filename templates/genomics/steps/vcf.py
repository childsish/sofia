import gzip
import os
from warnings import warn

from lhc.io.vcf_.index import IndexedVcfFile
from lhc.io.vcf_.iterator import VcfEntryIterator
from lhc.io.vcf_.set_ import VcfSet as VcfSetBase
from lhc.io.vcf_.tools.split_alt import _split_variant

from sofia import Resource, Target


class VcfIterator(Target):
    
    EXT = {'.vcf', '.vcf.gz'}
    FORMAT = 'vcf_file'
    OUT = ['variant']
    
    def get_interface(self, filename):
        self.variants = []
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return iter(VcfEntryIterator(fileobj))

    def calculate(self):
        if len(self.variants) == 0:
            self.variants = _split_variant(self.interface.next())
        return self.variants.pop()


class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = {'.vcf', '.vcf.gz'}
    FORMAT = 'vcf_file'
    OUT = ['variant_set']
    
    def get_interface(self, filename):
        if os.path.exists('{}.tbi'.format(filename)):
            try:
                import pysam
                return IndexedVcfFile(filename, pysam.TabixFile(filename))
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(filename)):
            from lhc.io.txt_ import index
            return IndexedVcfFile(filename, index.IndexedFile(filename))
        warn('no index available for {}, loading whole file...'.format(filename))
        return VcfSetBase(VcfEntryIterator(filename))
