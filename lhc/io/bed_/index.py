import json
import os

from Bio import bgzf
from iterator import BedLineIterator
from lhc.io.txt_.index import FileIndex


class IndexedBedFile(object):
    def __init__(self, fname):
        if not os.path.exists('{}.lci'.format(fname)):
            msg = 'Interval index missing. Try: "python -m lhc.io.bed index {}".'.format(fname)
            raise OSError(msg)
        self.fhndl = bgzf.open(fname)
        fhndl = open('{}.lci'.format(fname))
        self.index = FileIndex.init_from_state(json.load(fhndl))
        fhndl.close()
    
    def fetch(self, chr, start, stop):
        fr_fpos, fr_length = self.index[(chr, start)]
        to_fpos, to_length = self.index[(chr, stop)]
        self.fhndl.seek(fr_fpos)
        data = self.fhndl.read(fr_length)
        intervals = [BedLineIterator.parse_line(line) for line in data.split('\n') if line != '']
        return [interval for interval in intervals if interval.start < stop and interval.stop >= start]
