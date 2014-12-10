import os
import sys

from sofia_.action import Resource, Target

from modules.file_formats.vcf import VcfIterator as VcfIteratorParser, VcfSet as VcfSetParser

class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant']
    
    def init(self):
        self.parser = VcfIteratorParser(self.getFilename())

    def calculate(self):
        variant = self.parser.next()
        genomic_position = {'chromosome_id': variant.chr,
            'chromosome_pos': variant.pos}
        return {'genomic_position': genomic_position, 'variant': variant}

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant_set']
    
    def init(self, fr=None, to=None):
        fname = self.getFilename()
        if os.path.exists('%s.tbi'%fname):
            try:
                from lhc.file_format.vcf_.index import IndexedVcfFile
                self.parser = IndexedVcfFile(fname)
                return
            except ImportError:
                sys.stderr.write('Pysam not available. Parsing entire file.')
                pass
        self.parser = VcfSetParser(VcfIteratorParser(fname))
