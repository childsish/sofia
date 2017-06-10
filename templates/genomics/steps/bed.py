import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.bed.iterator import BedLineIterator
from sofia.step import Step


class BedIterator(Step):

    IN = ['bed_file']
    OUT = ['genomic_interval']

    def run(self, bed_file):
        bed_file = bed_file[0]
        fileobj = gzip.open(bed_file, 'rt') if bed_file.endswith('.gz') else open(bed_file, encoding='utf-8')
        for line in BedLineIterator(fileobj):
            yield line


class BedSet(Step):

    IN = ['bed_file']
    OUT = ['genomic_interval_set']

    def run(self, bed_file):
        bed_file = bed_file[0]
        fileobj = gzip.open(bed_file, 'rt') if bed_file.endswith('.gz') else open(bed_file, encoding='utf-8')
        yield InOrderAccessIntervalSet(BedLineIterator(fileobj))
