import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.bed_.iterator import BedLineIterator

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
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return InOrderAccessIntervalSet(BedLineIterator(fileobj), key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))
