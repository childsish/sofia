__author__ = 'Liam Childs'

from lhc.interval import Interval
from lhc.indices.bgzf import PointIndex, IntervalIndex


class IndexParser(object):

    TYPES = {
        str: PointIndex,  # (s)tring
        int: PointIndex,  # (i)nteger
        float: PointIndex,  # (f)loat
        Interval: IntervalIndex  # (r)ange
    }

    def __init__(self):
        self.pos = None

    def parse(self, definition):
        if definition.name == 'Entry':
            indices = tuple(self.TYPES[d.type] for d in definition.entities)
            return indices[0](indices[1:])
        return self.TYPES[definition.type]()

    @classmethod
    def register_index(cls, type, index):
        if type in cls.TYPES:
            raise KeyError('type "{}" already taken'.format(type))
        cls.TYPES[type] = index
