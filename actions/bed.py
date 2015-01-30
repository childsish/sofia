import os

from sofia_.action import Resource, Target
from lhc.io.bed_.iterator import BedLineIterator as BedIteratorParser
from lhc.io.bed_.set_ import BedSet as BedSetParser


class BedIterator(Target):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    OUT = ['genomic_interval']
    
    def init(self):
        self.parser = BedIteratorParser(self.get_filename())

    def calculate(self):
        interval = self.parser.next()
        return {
            'chromosome_id': interval.ivl.chr,
            'start': interval.ivl.start,
            'stop': interval.ivl.stop,
            'interval_name': interval.name
        }

    def format(self, genomic_interval):
        return genomic_interval['data'].name


class BedSet(Resource):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    OUT = ['genomic_interval_set']

    def init(self):
        fname = self.get_filename()
        if os.path.exists('{}.tbi'.format(fname)):
            try:
                from lhc.io.bed_.index import IndexedBedFile
            except ImportError:
                sys.stderr.write('Pysam not available. Bed file access will be slower.\n')
                IndexedBedFile = lambda fname: BedSetParser(BedIteratorParser(fname))
        else:
            IndexedBedFile = lambda fname: BedSetParser(BedIteratorParser(fname))
        self.parser = IndexedBedFile(fname)
