from collections import namedtuple
from lhc.binf.genomic_feature import GenomicFeature
from lhc.binf.genomic_coordinate import GenomicInterval as Interval


GffLine = namedtuple('GffLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))

GenomicFeatureTracker = namedtuple('GenomicFeatureTracker', ('interval', 'lines'))


class GffLineIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.line_no = 0

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

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t')
        parts[3] = int(parts[3]) - 1
        parts[4] = int(parts[4])
        parts[8] = GffLineIterator.parse_attributes(parts[8])
        return GffLine(*parts)

    @staticmethod
    def parse_attributes(attr):
        res = {}
        for part in attr.split(';'):
            if part == '':
                continue
            k, v = part.split('=', 1) if '=' in part else part
            res[k] = v.split(',') if ',' in v else v
        return res


class GffEntryIterator(object):
    def __init__(self, fname):
        self.it = GffLineIterator(fname)
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
                self.completed_features = self.get_features(lines)
                return self.completed_features
            lines.append(line)
            self.c_interval.union_update(line, compare_strand=False)
        self.c_line = []
        self.c_interval = None
        self.completed_features = self.get_features(lines)
        return self.completed_features

    @staticmethod
    def get_features(lines):
        top_features = {}
        open_features = {}
        for i, line in enumerate(lines):
            id = line.attr.get('ID', str(i))
            ivl = Interval(line.chr, line.start, line.stop, line.strand)
            name = line.attr.get('transcript_id', id).split('.')[0] if line.type in {'mRNA', 'exon', 'transcript'} else\
                line.attr.get('protein_id', id).split('.')[0] if line.type == 'CDS' else\
                line.attr.get('Name', id)
            feature = GenomicFeature(name, line.type, ivl, line.attr)
            if id in open_features:
                feature.children = open_features[id].children
            elif id in top_features:
                feature.children = top_features[id].children
            open_features[id] = feature
            if 'Parent' in line.attr:
                parents = line.attr['Parent'] if isinstance(line.attr['Parent'], list) else [line.attr['Parent']]
                for parent in parents:
                    if parent not in open_features:
                        open_features[parent] = GenomicFeature(parent)
                    open_features[parent].add_child(feature)
            else:
                top_features[id] = feature
        if len(top_features) == 0:
            return []
        return zip(*sorted(top_features.iteritems()))[1]
