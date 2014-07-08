from ebias.resource import ResourceIterator, ResourceSet

from lhc.file_format.gtf_.iterator import GtfIterator
from lhc.file_format.gtf_.set_ import GtfSet

class GtfIterator(ResourceIterator):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfIterator
    OUT = ['gene_model_iterator']

class GtfSet(ResourceSet):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfSet
    OUT = ['gene_model_set']
