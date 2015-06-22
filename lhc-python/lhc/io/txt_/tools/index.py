import json

from Bio import bgzf
from bisect import bisect_left
from lhc.io.txt_.tracker_factory import TrackerFactory
from lhc.interval import Interval


class FileIndex(object):
    def __init__(self, depth=1):
        self.depth = depth
        self.keys = []
        self.values = []

    def __getitem__(self, item):
        idx = self.get_index_below(item)
        value = self.values[idx]
        if self.depth == 1:
            return value
        return value[item[1:]]

    def __setitem__(self, key, value):
        idx = bisect_left(self.keys, key[0])
        if idx >= len(self.keys) or self.keys[idx] != key[0]:
            self.keys.insert(idx, key[0])
            self.values.insert(idx, value if self.depth == 1 else FileIndex(self.depth - 1))
        if self.depth > 1:
            self.values[idx][key[1:]] = value

    def get_key_below(self, item):
        idx = self.get_index_below(item)
        key = (self.keys[idx],)
        if self.depth == 1:
            return key
        return key + self.values[idx].get_key_below(item[1:])

    def get_index_below(self, item):
        idx = bisect_left(self.keys, item[0])
        if self.depth > 1 and idx >= len(self.keys):
            raise KeyError(str(item[0]))
        elif idx < len(self.keys) and self.keys[idx] != item[0]:
            idx -= 1
        elif self.depth == 1 and idx >= len(self.keys):
            idx -= 1
        return idx


    def __getstate__(self):
        values = self.values if self.depth == 1 else [value.__getstate__() for value in self.values]
        return {
            'depth': self.depth,
            'keys': self.keys,
            'values': values
        }

    def __setstate__(self, state):
        self.depth = state['depth']
        self.keys = state['keys']
        self.values = state['values'] if self.depth == 1 else\
            [self.init_from_state(state, self.depth - 1) for state in state['values']]

    @staticmethod
    def init_from_state(state, depth=0):
        index = FileIndex(depth)
        index.__setstate__(state)
        return index


class IndexedFile(object):
    def __init__(self, fname):
        self.fhndl = bgzf.open(fname)
        fhndl = open('{}.lci'.format(fname))
        index_context = json.load(fhndl)
        fhndl.close()
        factory = TrackerFactory()
        self.trackers = [factory.make(definition) for definition in index_context['column_types']]
        self.index = FileIndex.init_from_state(index_context['index'])

    def fetch(self, *args):
        """ Fetch the lines matching the given arguments
        Supports an interval as the last two parameters instead of a single value.
        eg. fetch('chr1', 100) returns the lines overlapping a single point
            fetch('chr1', 100, 200) returns the lines overlapping an interval
            fetch('chr1') is currently invalid
            fetch('chr1', 'chr2', 100) is invalid
            fetch('chr1', 'chr2', 100, 200) is invalid

        :param args: keys that the fetched lines must match
        :return: list of matched lines
        """
        nargs = len(args)
        depth = self.index.depth
        if nargs < depth or nargs > depth + 1:
            raise KeyError('number of given keys and required keys in index do not match')
        elif nargs == depth:
            fpos, length = self.index[args]
            ivl = Interval(args[-1], args[-1])
            args = args[:-1]
        else:
            fpos, length = self.index[args[:-1]]
            ivl = Interval(args[-2], args[-1])
            args = args[:-2]

        self.fhndl.seek(fpos)
        lines = []
        for line in self.fhndl:
            parts = line.rstrip('\r\n').split('\t')
            keys = [tracker.convert(parts) for tracker in self.trackers]
            if all(arg == key for arg, key in zip(args, keys[:-1])) and self.trackers[-1].overlaps(ivl, keys[-1]):
                lines.append(line)
            elif any(arg < key for arg, key in zip(args, keys[:-1])) and self.trackers[-1].passed(ivl, keys[-1]):
                break
        return lines
