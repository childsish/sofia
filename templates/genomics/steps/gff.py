import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet as IntervalSet
from lhc.interval import Interval
from lhc.io.gff_.iterator import GffEntryIterator

from sofia.step import Resource, Target


class GffIterator(Target):
    
    EXT = {'.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz'}
    FORMAT = 'gff_file'
    OUT = ['genomic_feature']

    def get_interface(self, filename):
        return iter(GffEntryIterator(filename))

    def calculate(self):
        entry = self.interface.next()
        while entry.type != 'gene':
            entry = self.interface.next()
        entry.name = entry.name.rsplit('.', 1)[0]
        return entry


class GffSet(Resource):
    
    EXT = ['.gff', '.gff.gz', '.gff.bgz', '.gff3', '.gff3.gz', '.gff3.bgz']
    FORMAT = 'gff_file'
    OUT = ['genomic_feature_set']

    def get_interface(self, filename):
        fileobj = gzip.open(filename) if filename.endswith('.gz') else\
            open(filename)
        return IntervalSet(GffEntryIterator(fileobj), key=lambda x: Interval((x.chr, x.start), (x.chr, x.stop)))
