from ebias.resource import Resource

from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser
from lhc.file_format.vcf_.index import IndexedVcfFile

class VcfIterator(Resource):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIteratorParser
    TARGET = True
    OUT = ['variant_iterator']

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz', '.vcf.idx']
    TYPE = 'variant'
    PARSER = VcfSetParser
    OUT = ['variant_set']
    
    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedVcfFile(fname) if fname.endswith('.gtf.idx') else\
            VcfSetParser(VcfIteratorParser(fname))

