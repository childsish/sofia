from ebias.resource_feature import ResourceFeature

from lhc.file_format.gtf_.iterator import GtfIterator as GtfIteratorParser
from lhc.file_format.gtf_.set_ import GtfSet as GtfSetParser

class GtfIterator(ResourceFeature):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfIteratorParser
    OUT = ['gene_model_iterator']

class GtfSet(ResourceFeature):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfSetParser
    OUT = ['gene_model_set']
