from ebias.resource import Resource, Target

from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser
from lhc.file_format.vcf_.index import IndexedVcfFile

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
    
    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedVcfFile(fname) if fname.endswith('.gtf.idx') else\
            VcfSetParser(VcfIteratorParser(fname))

