from ebias.resource_feature import ResourceFeature

from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser

class VcfIterator(ResourceFeature):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIteratorParser
    OUT = ['variant_iterator']

class VcfSet(ResourceFeature):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfSetParser
    OUT = ['variant_set']
