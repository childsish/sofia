from sofia_.action import Resource, Target
from lhc.io.gtf_.iterator import GtfEntityIterator as GtfIteratorParser
from lhc.io.gtf_.set_ import GtfSet as GtfSetParser


class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz']
    OUT = ['gene_model']

    def init(self):
        self.parser = GtfIteratorParser(self.get_filename())


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    OUT = ['gene_model_set']

    def init(self):
        try:
            from lhc.io.gtf_.index import IndexedGtfFile
        except ImportError:
            import sys
            sys.stderr.write('Pysam not available. Gtf file access will be slower.\n')
            IndexedGtfFile = lambda fname: GtfSetParser(GtfIteratorParser(fname))
        self.parser = IndexedGtfFile(self.get_filename())