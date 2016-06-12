import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.bed.iterator import BedLineIterator
from sofia.step import Step


class BedIterator(Step):

    IN = ['bed_file']
    OUT = ['genomic_interval']
    
    def run(self, bed_file):
        fileobj = gzip.open(bed_file) if bed_file.endswith('.gz') else open(bed_file)
        for line in BedLineIterator(fileobj):
            yield line


class BedSet(Step):

    IN = ['bed_file']
    OUT = ['genomic_interval_set']

    def run(self, bed_file):
        fileobj = gzip.open(bed_file) if bed_file.endswith('.gz') else open(bed_file)
        yield InOrderAccessIntervalSet(BedLineIterator(fileobj), key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))
