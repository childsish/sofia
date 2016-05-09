import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.gtf.iterator import GtfEntryIterator

from sofia.step import Resource, Target


class GtfIterator(Target):
    
    EXT = {'.gtf', '.gtf.gz', '.gtf.bgz'}
    FORMAT = 'gtf_file'
    OUT = ['genomic_feature']

    def get_interface(self, filename):
        return GtfEntryIterator(filename)

    def calculate(self):
        try: #REMOVEME
            entry = self.interface.next()
        except Exception:
            return None
        while entry.type != 'gene':
            entry = self.interface.next()
        entry.name = entry.name.rsplit('.')[0]
        return entry


class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz', '.gtf.bgz']
    FORMAT = 'gtf_file'
    OUT = ['genomic_feature_set']

    def get_interface(self, filename):
        fileobj = gzip.open(filename) if filename.endswith('.gz') else open(filename)
        return InOrderAccessIntervalSet(GtfEntryIterator(fileobj), key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))
