import json
import os

from Bio import bgzf
from iterator import BedLineIterator
from lhc.io.txt_.index import FileIndex


class IndexedBedFile(object):
    def __init__(self, fname):
        self.fhndl = bgzf.open(fname)
        if not os.path.exists('{}.lci'.format(fname)):
            msg = 'Interval index missing. Try: "python -m lhc.io.bed index {}".'.format(fname)
            raise OSError(msg)
        fhndl = open('{}.lci'.format(fname))
        self.index = FileIndex.init_from_state(json.load(fhndl))
        fhndl.close()
    
    def fetch(self, chr, start, stop):
        fpos, length = self.index[(chr, start)]
        self.fhndl.seek(fpos)
        data = self.fhndl.read(length)
        intervals = [BedLineIterator.parse_line(line) for line in data.split('\n') if line != '']
        return [interval for interval in intervals if interval.start < stop and interval.stop >= start]
