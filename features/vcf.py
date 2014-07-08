from ebias.resource import ResourceIterator, ResourceSet

from lhc.file_format.vcf_.iterator import VcfIterator
from lhc.file_format.vcf_.set_ import VcfSet

class VcfIterator(ResourceIterator):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIterator
    OUT = ['variant_iterator']

class VcfSet(ResourceSet):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfSet
    OUT = ['variant_set']
