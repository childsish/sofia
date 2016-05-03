from collections import namedtuple
from itertools import chain
from lhc.binf.genomic_feature import GenomicFeature
from lhc.binf.genomic_coordinate import GenomicInterval as Interval


GtfLine = namedtuple('GtfLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))

GenomicFeatureTracker = namedtuple('GenomicFeatureTracker', ('interval', 'lines'))


class GtfLineIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.line_no = 0
        self.hdr = self.parse_header()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        while True:
            line = self.parse_line(self.iterator.next())
            self.line_no += 1
            if line.type != 'chromosome':
                break
        return line

    def close(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()

    def parse_header(self):
        hdrs = []
        line = self.iterator.next()
        line_no = 1
        while line.startswith('#'):
            hdrs.append(line)
            line = self.iterator.readline()
            line_no += 1
        self.line_no = line_no
        self.iterator = chain([line], self.iterator)
        return hdrs

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        parts[3] = int(parts[3]) - 1
        parts[4] = int(parts[4])
        parts[8] = GtfLineIterator.parse_attributes(parts[8])
        return GtfLine(*parts)

    @staticmethod
    def parse_attributes(attr):
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)


class GtfEntryIterator(object):
    def __init__(self, fname):
        self.it = GtfLineIterator(fname)
        self.completed_features = []
        self.c_feature = 0
        line = self.it.next()
        self.c_line = [line]
        self.c_interval = Interval(line.chr, line.start, line.stop)

    def __iter__(self):
        return self

    @property
    def line_no(self):
        return self.it.line_no

    def next(self):
        completed_features = self.get_completed_features()
        if self.c_feature >= len(completed_features):
            raise StopIteration
        feature = completed_features[self.c_feature]
        self.c_feature += 1
        return feature

    def get_completed_features(self):
        if self.c_feature < len(self.completed_features):
            return self.completed_features

        self.c_feature = 0
        lines = self.c_line
        for line in self.it:
            if not self.c_interval.overlaps(line):
                self.c_line = [line]
                self.c_interval = Interval(line.chr, line.start, line.stop)
                self.completed_features = self.get_features_raw(lines)
                return self.completed_features
            lines.append(line)
            self.c_interval.union_update(line, compare_strand=False)
        self.c_line = []
        self.c_interval = None
        self.completed_features = self.get_features_raw(lines)
        return self.completed_features

    @staticmethod
    def get_features(lines):
        return GtfEntryIterator.get_features_raw(GtfLineIterator.parse_line(line) for line in lines)

    @staticmethod
    def get_features_raw(lines):
        top_features = {}
        open_features = {}
        for i, line in enumerate(lines):
            id = line.attr['gene_name'] if line.type == 'gene' else\
                line.attr['transcript_id'] if line.type == 'transcript' else\
                i
            ivl = Interval(line.chr, line.start, line.stop, line.strand)
            feature = GenomicFeature(id, line.type, ivl, line.attr)
            open_features[id] = feature
            if line.type != 'gene':
                parent = line.attr['gene_name'] if line.type == 'transcript' else\
                    line.attr['transcript_id']
                if parent not in open_features:
                    open_features[parent] = GenomicFeature(parent)
                open_features[parent].add_child(feature)
            else:
                top_features[id] = feature
        if len(top_features) == 0:
            return []
        return zip(*sorted(top_features.iteritems()))[1]
