import os
import sys

from ebias.features import Resource, Target

from lhc.file_format.bed_.iterator import BedIterator as BedIteratorParser
from lhc.file_format.bed_.set_ import BedSet as BedSetParser

class BedIterator(Target):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    PARSER = BedIteratorParser
    OUT = ['genomic_interval']

class BedSet(Resource):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    PARSER = BedSetParser
    OUT = ['genomic_interval_set']

    def init(self):
        fname = self.getFilename()
        if os.path.exists('%s.tbi'%fname):
            try:
                from lhc.file_format.bed_.index import IndexedBedFile
                self.parser = IndexedBedFile(fname)
                return
            except ImportError:
                sys.stderr.write('Pysam not available. Parsing entire file.')
                pass
        self.parser = BedSetParser(BedIteratorParser(fname))

