from bisect import bisect_left, bisect_right
from operator import add
from lhc.interval import Interval


class TrackedIndex(object):
    def __init__(self, n):
        self.n = n
        self.tracks = [Track(n)]

    def add(self, item, offset):
        cost_increases = [(track.get_cost_increase(item), i) for i, track in enumerate(self.tracks)]
        min_increase, index = min(cost_increases)
        self.tracks[index].add(item, offset)
        if index == len(self.tracks) - 1:
            self.tracks.append(Track(self.n))

    def fetch(self, *args):
        return reduce(add, (track.fetch(*args) for track in self.tracks))


class Track(object):
    def __init__(self, n):
        self.starts = []
        self.stops = []
        self.offsets = []
        self.n = n

    def add(self, interval, offset):
        """
        The added interval must be overlapping or beyond the last stored interval ie. added in sorted order.

        :param interval: interval to add
        :param offset: full virtual offset to add
        :return:
        """
        start, stop = self.get_start_stop(interval)

        if len(self.starts) > 0:
            if start < self.starts[-1] or offset <= self.offsets[-1][1]:
                raise ValueError('intervals and offsets must be added in-order')
            self.offsets[-1][1] = offset
            self.offsets[-1][2] += 1
        else:
            self.starts.append(start)
            self.stops.append(stop)
            self.offsets.append([offset, offset, 1])

    def fetch(self, *args):
        start, stop = self.get_start_stop(args)
        fr, to = self.get_overlapping_bounds(start, stop)
        return [self.offsets[i] for i in xrange(fr, to)]

    def get_overlapping_bounds(self, start, stop):
        return bisect_right(self.stops, start), bisect_left(self.starts, stop)

    def get_start_stop(self, item):
        start = [item[i].start if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        stop = [item[i].stop if isinstance(item[i], Interval) else item[i] for i in xrange(self.n)]
        if len(item) == self.n + 1:
            stop[-1] = item[-1]
        return start, stop

    def get_cost_increase(self, interval):
        if len(self.offsets) == 0:
            return 50
        start, stop = self.get_start_stop(interval)
        if start < self.starts[-1]:
            raise ValueError('intervals must be added in-order')
        return self.offsets[-1][2] if start < self.stops[-1] else 0


def save_index(fileobj, index):
    import json

    json.dump({
        'n': index.n,
        'tracks': [
            {'n': track.n,
             'starts': track.starts,
             'stops': track.stops,
             'offsets': track.offsets} for track in index.tracks
        ]
    }, fileobj)


def load_index(fileobj):
    import json

    data = json.load(fileobj)
    index = TrackedIndex(data['n'])
    for track_data in data['tracks']:
        track = Track(track_data['n'])
        track.starts = track_data['starts']
        track.stops = track_data['stops']
        track.offsets = track_data['offsets']
        index.tracks.append(track)
    return index
