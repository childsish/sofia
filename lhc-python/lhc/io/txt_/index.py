import itertools

from bisect import bisect_left


class FileIndex(object):
    def __init__(self, depth=1):
        self.depth = depth
        self.keys = []
        self.values = []

    def __getitem__(self, item):
        idx = bisect_left(self.keys, item[0])
        if self.depth > 1 and idx >= len(self.keys):
            raise KeyError(str(item[0]))
        elif self.depth == 1 and idx >= len(self.keys):
            idx -= 1
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
