from sofia_.action import Resource, Target
from lhc.file_format.gtf_.iterator import GtfEntityIterator as GtfIteratorParser
from lhc.file_format.gtf_.set_ import GtfSet as GtfSetParser
try:
    from lhc.file_format.gtf_.index import IndexedGtfFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Gtf file access will be slower.\n')
    IndexedGtfFile = lambda fname: GtfSetParser(GtfIteratorParser(fname))


class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_iterator']

    def init(self):
        self.parser = GtfIteratorParser(self.get_filename())


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_set']

    def init(self):
        self.parser = IndexedGtfFile(self.get_filename())
