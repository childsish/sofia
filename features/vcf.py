from ebias.resource import Resource

from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser

class VcfIterator(Resource):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIteratorParser
    OUT = ['variant_iterator']
    
    def init(self, **kwargs):
        self.parser = VcfIteratorParser(self.resource.fname)

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfSetParser
    OUT = ['variant_set']
    
    def init(self, **kwargs):
        self.parser = VcfSetParser(VcfIteratorParser(self.resource.fname))
