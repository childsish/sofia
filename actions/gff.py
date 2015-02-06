from sofia_.action import Resource, Target
from lhc.io.gff_.iterator import GffEntityIterator as GffIteratorParser
from lhc.io.gff_.set_ import GffSet as GffSetParser


class GffIterator(Target):
    
    EXT = ['.gff', '.gff.gz']
    OUT = ['gene_model']

    def init(self):
        self.parser = GffIteratorParser(self.get_filename())


class GffSet(Resource):
    
    EXT = ['.gff', '.gff.gz']
    OUT = ['gene_model_set']

    def init(self):
        try:
            from lhc.io.gff_.index import IndexedGffFile
        except ImportError:
            import sys
            sys.stderr.write('Pysam not available. Gff file access will be slower.\n')
            IndexedGffFile = lambda fname: GffSetParser(GffIteratorParser(fname))
        self.parser = IndexedGffFile(self.get_filename())
