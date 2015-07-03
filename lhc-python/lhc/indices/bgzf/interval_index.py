__author__ = 'Liam Childs'

from operator import or_
from lhc.indices.bgzf.track import Track


class IntervalIndex(object):
    def __init__(self, index_classes=[], max_tracks=None):
        self.tracks = []
        self.index_classes = index_classes
        self.max_tracks = max_tracks

    def __contains__(self, item):
        return any(item in track for track in self.tracks)

    def __or__(self, other):
        if self.index_classes != other.index_classes:
            raise TypeError('incompatible index merge {} vs. {}'.format(self.index_classes, other.index_classes))
        res = IntervalIndex(self.index_classes)
        res.tracks = self.tracks + other.tracks
        res.max_tracks = max(len(res.tracks), self.max_tracks, other.max_tracks)
        return res

    def add(self, key, value):
        last_index = len(self.tracks)
        costs = [(track.get_cost(key, value) - track.get_cost(), i) for i, track in enumerate(self.tracks)]
        if self.max_tracks is None or len(self.tracks) < self.max_tracks:
            costs.insert(0, (1, last_index))
        idx = sorted(costs, key=lambda x: x[0])[0][1]
        if idx == last_index:
            self.tracks.append(Track(self.index_classes))
        self.tracks[idx].add(key, value)

    def fetch(self, *args):
        return reduce(or_, (track.fetch(*args) for track in self.tracks))

    def get_cost(self, key=None, value=None):
        return max(track.get_cost(key, value) for track in self.tracks)

    def compress(self, factor):
        for i, track in enumerate(self.tracks):
            self.tracks[i] = track.compress(factor)
        return self

    # pickle helpers

    def __getstate__(self):
        return {
            'type': type(self),
            'tracks': [track.__getstate__() for track in self.tracks],
            'index_classes': self.index_classes,
            'max_tracks': self.max_tracks
        }

    def __setstate__(self, state):
        self.index_classes = state['index_classes']
        self.max_tracks = state['max_tracks']
        self.tracks = [self.init_from_state(state, self.index_classes) for state in state['tracks']]

    @staticmethod
    def init_from_state(state, index_classes):
        index = index_classes[0](index_classes[1:])
        index.__setstate__(state)
        return index
