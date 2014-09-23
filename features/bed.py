import os
import sys

from ebias.resource import Resource, Target

from lhc.file_format.bed_.iterator import BedIterator as BedIteratorParser
from lhc.file_format.bed_.set_ import BedSet as BedSetParser

class BedIterator(Target):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    PARSER = BedIteratorParser
    TARGET = True
    OUT = ['genomic_interval_iterator']

class BedSet(Resource):
    
    EXT = ['.bed', '.bed.gz']
    TYPE = 'genomic_interval'
    PARSER = BedSetParser
    OUT = ['genomic_interval_set']

    def init(self):
        fname = self.getFilename()
        if fname.endswith('.gz'):
            from lhc.file_format.bed_.index import IndexedBedFile
        self.parser = IndexedBedFile(fname) if os.path.exists('%s.tbi'%fname)\
            else BedSetParser(BedIteratorParser(fname))
