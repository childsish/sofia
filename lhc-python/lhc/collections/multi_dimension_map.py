__author__ = 'Liam Childs'

from lhc.collections.interval_map import IntervalMap
from lhc.interval import Interval


class MultiDimensionMap(object):
    def __init__(self, dimension_classes, key_value_pairs=None):
        self.len = 0
        self.child_classes = [IntervalMap if class_ is Interval else dict for class_ in dimension_classes]
        self.root = Dimension(self.child_classes[0], self.child_classes[1:])

        if key_value_pairs is not None:
            for key, value in key_value_pairs:
                self[key] = value

    def __len__(self):
        return self.len

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, key, value):
        self.root[key] = value
        self.len += 1


class Dimension(object):
    def __init__(self, map_class, child_classes):
        self.map = map_class()
        self.child_classes = child_classes
        self.is_last = len(child_classes) == 0

    def __contains__(self, item):
        if item[0] not in self.map:
            return False
        return True if self.is_last else item[1:] in self.map[item[0]]

    def __getitem__(self, item):
        if self.is_last:
            return self.map[item[0]]
        return self.map[item[0]][item[1:]]

    def __setitem__(self, key, value):
        if self.is_last:
            self.map[key[0]] = value
        else:
            if key[0] not in self.map:
                self.map[key[0]] = Dimension(self.child_classes[0], self.child_classes[1:])
            self.map[key[0]][key[1:]] = value
