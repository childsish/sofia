import re

from lhc.interval import Interval
from column_tracker import KeyColumnTracker, IntervalColumnTracker


class TrackerFactory(object):

    REGX = re.compile('\d+')

    TYPES = {
        's': (KeyColumnTracker, str),
        'f': (KeyColumnTracker, float),
        'i': (KeyColumnTracker, int),
        'v': (IntervalColumnTracker, lambda start, stop: Interval(int(start), int(stop)))
    }

    def make(self, definition='1s'):
        tracker, type = self.TYPES[definition[-1]]
        columns = [int(column) - 1 for column in self.REGX.findall(definition[:-1])]
        return tracker(columns, type)
