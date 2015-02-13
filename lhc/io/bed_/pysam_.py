import pysam

from iterator import BedLineIterator


class BedPysamWrapper(object):
    def __init__(self, fname):
        self.fhndl = pysam.TabixFile(fname)

    def fetch(self, chr, start, stop):
        return [BedLineIterator.parse_line(line) for line in self.fhndl.fetch(chr, start, stop)]
