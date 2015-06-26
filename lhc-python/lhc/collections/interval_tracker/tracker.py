__author__ = 'Liam Childs'

from .track import Track
from operator import or_


class IntervalTracker(object):
    def __init__(self, intervals=[], max_tracks=None):
        self.tracks = []
        self.max_tracks = max_tracks

        for interval in intervals:
            self[interval] = interval.data

    def __contains__(self, item):
        return any(item in track for track in self.tracks)

    def __getitem__(self, item):
        return reduce(or_, (track[item] for track in self.tracks))

    def __setitem__(self, key, value):
        last_index = len(self.tracks)
        costs = [(track.get_cost(key, value) - track.get_cost(), i) for i, track in enumerate(self.tracks)]
        if self.max_tracks is None or len(self.tracks) < self.max_tracks:
            costs.insert(0, (1, last_index))
        idx = sorted(costs, key=lambda x: x[0])[0][1]
        if idx == last_index:
            self.tracks.append(Track())
        self.tracks[idx][key] = value
