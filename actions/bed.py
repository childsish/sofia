from sofia_.action import Resource, Target
from modules.file_formats.bed_.iterator import BedIterator as BedIteratorParser
from modules.file_formats.bed_.set_ import BedSet as BedSetParser
try:
    from modules.file_formats.bed_.index import IndexedBedFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Bed file access will be slower.\n')
    IndexedBedFile = lambda fname: BedSetParser(BedIteratorParser(fname))


class BedIterator(Target):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    OUT = ['genomic_interval']
    
    def init(self):
        self.parser = BedIteratorParser(self.getFilename())

    def calculate(self):
        interval = self.parser.next()
        return {
            'chromosome_id': interval.chr,
            'start': interval.start,
            'stop': interval.stop,
            'data': interval
        }

    def format(self, genomic_interval):
        return genomic_interval['data'].name


class BedSet(Resource):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    OUT = ['genomic_interval_set']

    def init(self):
        self.parser = IndexedBedFile(fname)
