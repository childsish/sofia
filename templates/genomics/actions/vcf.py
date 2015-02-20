import os

from sofia_.action import Resource, Target
from lhc.io.vcf_.index import IndexedVcfFile
from lhc.io.vcf_.iterator import VcfEntryIterator
from lhc.io.vcf_.set_ import VcfSet as VcfSetBase
from warnings import warn


class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant']
    
    def init(self):
        self.parser = iter(VcfEntryIterator(self.get_filename()))

    def calculate(self):
        variant = self.parser.next()
        return {
            'genomic_position': {
                'chromosome_id': variant.chr,
                'chromosome_pos': variant.pos
            },
            'ref': variant.ref,
            'alt': variant.alt,
            'qual': variant.qual,
            'info': variant.info,
            'samples': variant.samples
        }


class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant_set']
    
    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                import pysam
                self.parser = IndexedVcfFile(pysam.TabixFile(fname))
                return
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(fname)):
            from lhc.io.txt_ import index
            self.parser = IndexedVcfFile(index.IndexedFile(fname))
            return
        warn('no index available for {}, loading whole file...'.format(fname))
        self.parser = VcfSetBase(VcfEntryIterator(fname))
