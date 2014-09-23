import os

from ebias.resource import Resource, Target

from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser

class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIteratorParser
    TARGET = True
    OUT = ['variant', 'genomic_position']

    def calculate(self):
        return self.parser.next()

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfSetParser
    OUT = ['variant_set']
    
    def init(self, style='ensemble', ignore=''):
        fname = self.getFilename()
        if fname.endswith('.gz'):
            from lhc.file_format.vcf_.index import IndexedVcfFile
        self.parser = IndexedVcfFile(fname, style, ignore.split('-'))\
            if os.path.exists('%s.tbi'%fname) else\
            VcfSetParser(VcfIteratorParser(fname))
