from sofia_.action import Resource, Target
from modules.file_formats.gtf_.iterator import GtfIterator as GtfIteratorParser
from modules.file_formats.gtf_.set_ import GtfSet as GtfSetParser
try:
    from modules.file_formats.gtf_.index import IndexedGtfFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Gtf file access will be slower.')
    IndexedGtfFile = lambda fname: GtfSetParser(GtfIteratorParser(fname))


class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_iterator']

    def init(self):
        self.parser = GtfIteratorParser(self.getFilename())


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_set']

    def init(self):
        self.parser = IndexedGtfFile(self.getFilename())
