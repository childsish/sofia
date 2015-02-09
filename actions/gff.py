from sofia_.action import Resource, Target
from lhc.io.gff_.iterator import GffEntryIterator as GffIteratorParser
from lhc.io.gff_.set_ import GffSet as GffSetParser


class GffIterator(Target):
    
    EXT = ['.gff', '.gff.gz']
    OUT = ['genomic_feature']

    def init(self):
        self.parser = iter(GffIteratorParser(self.get_filename()))

    def calculate(self):
        entry = self.parser.next()
        while entry.type != 'gene':
            entry = self.parser.next()
        return {
            'gene_id': entry.name,
            'genomic_interval': {
                'chromosome_id': entry.chr,
                'start': entry.start,
                'stop': entry.stop
            },
            'data': entry
        }


class GffSet(Resource):
    
    EXT = ['.gff', '.gff.gz']
    OUT = ['genomic_feature_set']

    def init(self):
        try:
            from lhc.io.gff_.index import IndexedGffFile
        except ImportError:
            import sys
            sys.stderr.write('Pysam not available. Gff file access will be slower.\n')
            IndexedGffFile = lambda fname: GffSetParser(GffIteratorParser(fname))
        self.parser = IndexedGffFile(self.get_filename())
