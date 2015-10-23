__author__ = 'Liam Childs'

from lhc.collections.interval_map import IntervalMap
from lhc.interval import Interval


class MultiDimensionMap(object):
    def __init__(self, dimension_classes, key_value_pairs=None):
        self.len = 0
        self.child_dimensions = [IntervalDimension if class_ is Interval else KeyDimension for class_ in dimension_classes]
        self.root = self.child_dimensions[0](self.child_dimensions[1:])

        if key_value_pairs is not None:
            for key, value in key_value_pairs:
                self[key] = value

    def __len__(self):
        return self.len

    def __iter__(self):
        for item in self.root:
            yield item

    def __contains__(self, item):
        return item in self.root

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, key, value):
        self.root[key] = value
        self.len += 1


class Dimension(object):
    def __init__(self, map_class, child_dimensions):
        self.map = map_class()
        self.child_dimensions = child_dimensions
        self.is_last = len(child_dimensions) == 0

    def __iter__(self):
        if self.is_last:
            for key in self.map.iterkeys():
                yield [key]
        else:
            for key, values in self.map.iteritems():
                for value in values:
                    yield [key] + value

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
                self.map[key[0]] = self.child_dimensions[0](self.child_dimensions[1:])
            self.map[key[0]][key[1:]] = value


class KeyDimension(Dimension):
    def __init__(self, child_dimensions):
        super(KeyDimension, self).__init__(dict, child_dimensions)

    def __getitem__(self, item):
        if item[0] in self.map:
            if self.is_last:
                yield self.map[item[0]]
            else:
                for value in self.map[item[0]][item[1:]]:
                    yield value


class IntervalDimension(Dimension):
    def __init__(self, child_dimensions):
        super(IntervalDimension, self).__init__(IntervalMap, child_dimensions)

    def __getitem__(self, item):
        values = self.map[item[0]] if self.is_last else self.map[item[0]][item[1:]]
        for value in values:
            yield value
