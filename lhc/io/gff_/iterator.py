from collections import namedtuple
from lhc.binf.genomic_feature import GenomicFeature
from lhc.binf.genomic_coordinate import Interval
from lhc.filetools.flexible_opener import open_flexibly


GffLine = namedtuple('GffLine', ('chr', 'source', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'))

GenomicFeatureTracker = namedtuple('GenomicFeatureTracker', ('interval', 'lines'))


class GffLineIterator(object):
    def __init__(self, fname):
        self.fname, self.fhndl = open_flexibly(fname)

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def next(self):
        return self.parse_line(self.fhndl.next())

    def close(self):
        if hasattr(self.fhndl, 'close'):
            self.fhndl.close()

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
        self.top_features = {}
        self.open_features = {}
        self.completed_features = []
        self.line_no = 0

    def __iter__(self):
        return self

    def next(self):
        completed_features = self.get_completed_features()
        while len(completed_features) > 0:
            feature = completed_features.pop()
            self.remove_feature(feature)
            return feature
        raise StopIteration()

    def get_completed_features(self):
        if len(self.completed_features) != 0:
            return self.completed_features

        top_features = self.top_features
        open_features = self.open_features
        for line in self.it:
            self.line_no += 1
            if line.type == 'chromosome':
                continue
            id = line.attr['ID'] if 'ID' in line.attr else self.line_no
            ivl = Interval(line.chr, line.start, line.stop, line.strand)
            tracker = GenomicFeatureTracker(ivl, [line])
            open_features[id] = tracker
            if 'Parent' in line.attr:
                parents = line.attr['Parent'] if isinstance(line.attr['Parent'], list) else [line.attr['Parent']]
                for parent in parents:
                    if parent not in open_features:
                        self.open_features[parent] = GenomicFeatureTracker(ivl, [])
                    self.open_features[parent].lines.append(line)
            else:
                top_features[id] = tracker
            self.completed_features = [self.get_features(tracker.lines)[0] for tracker in top_features.itervalues()
                                       if tracker.interval.stop <= line.start]
            if len(self.completed_features) > 0:
                return self.completed_features
        self.completed_features = [self.get_features(tracker.lines)[0] for tracker in top_features.itervalues()]
        return self.completed_features

    def remove_feature(self, feature):
        self.top_features.pop(feature.name, None)
        open_features = self.open_features
        stk = [feature]
        while len(stk) > 0:
            feature = stk.pop()
            open_features.pop(feature.name, None)
            stk.extend(feature.children)
            stk.extend(feature.products)

    @staticmethod
    def get_features(lines):
        top_features = {}
        open_features = {}
        for i, line in enumerate(lines):
            id = line.attr['ID'] if 'ID' in line.attr else i
            ivl = Interval(line.chr, line.start, line.stop, line.strand)
            feature = GenomicFeature(id, line.type, ivl, line.attr)
            open_features[id] = feature
            if 'Parent' in line.attr:
                parents = line.attr['Parent'] if isinstance(line.attr['Parent'], list) else [line.attr['Parent']]
                for parent in parents:
                    if parent not in open_features:
                        open_features[parent] = GenomicFeature(parent)
                    open_features[parent].add_child(feature)
            else:
                top_features[id] = feature
        return top_features.values()
