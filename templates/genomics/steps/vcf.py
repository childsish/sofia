import os

from sofia_.step import Resource, Target
from lhc.io.vcf_.tools.index import IndexedVcfFile
from lhc.io.vcf_.iterator import VcfEntryIterator
from lhc.io.vcf_.set_ import VcfSet as VcfSetBase
from warnings import warn


class VcfIterator(Target):
    
    EXT = {'.vcf', '.vcf.gz'}
    FORMAT = 'vcf'
    OUT = ['variant']
    
    def init(self):
        self.parser = iter(VcfEntryIterator(self.get_filename()))
        self.variant = None
        self.c_alt = 0
        self.alts = []
        self.arrays = []

    def calculate(self):
        if self.c_alt == len(self.alts):
            self.variant = self.parser.next()
            self.c_alt = 0
            self.alts = self.variant.alt.split(',')
            self.arrays = []
            for sample in self.variant.samples:
                for k, v in self.variant.samples[sample].iteritems():
                    if ',' in v:
                        self.arrays.append((sample, k, v.split(',')))
        res = self.variant._replace(alt=self.alts[self.c_alt])
        for sample, k, vs in self.arrays:
            res.samples[sample][k] = vs[self.c_alt]
        self.c_alt += 1
        return res


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
