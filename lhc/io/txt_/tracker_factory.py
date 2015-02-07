from lhc.interval import Interval
from column_tracker import KeyColumnTracker, IntervalColumnTracker


class TrackerFactory(object):

    TYPES = {
        's': (KeyColumnTracker, str),
        'f': (KeyColumnTracker, float),
        'i': (KeyColumnTracker, int),
        'v': (IntervalColumnTracker, lambda x: Interval(*x))
    }

    def make(self, definition='s1'):
        tracker, type = self.TYPES[definition[-1]]
        columns = [int(column) - 1 for column in definition[:-1].split(',')]
        return tracker(columns, type)
