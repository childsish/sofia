import os
from warnings import warn

from lhc.io.bed_.index import IndexedBedFile
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet as BedSetBase

from sofia.step import Resource, Target


class BedIterator(Target):
    
    EXT = {'.bed', '.bed.gz'}
    FORMAT = 'bed_file'
    OUT = ['genomic_interval']
    
    def get_interface(self, filename):
        return BedLineIterator(filename)


class BedSet(Resource):
    
    EXT = {'.bed', '.bed.gz', '.bed.bgz'}
    FORMAT = 'bed_file'
    OUT = ['genomic_interval_set']

    def get_interface(self, filename):
        if os.path.exists('{}.tbi'.format(filename)):
            try:
                import pysam
                return IndexedBedFile(pysam.TabixFile(filename))
            except ImportError:
                pass
        if os.path.exists('{}.lci'.format(filename)):
            from lhc.io.txt_ import index
            return IndexedBedFile(index.IndexedFile(filename))
        warn('no index available for {}, loading whole file...'.format(filename))
        return BedSetBase(BedLineIterator(filename))
