from itertools import chain
from operator import ge, gt


class InOrderAccessSet(object):
    def __init__(self, iterator, key=None):
        self.key_fn = [lambda x: x] if key is None else key

        self.keys = []
        self.buffer = []
        self.iterator = iterator

    def fetch(self, *args):
        if len(args) not in (len(self.key_fn), len(self.key_fn) + 1):
            msg = 'invalid number of dimensions. expected {} or {}, got {}'
            raise ValueError(msg.format(len(self.key_fn), len(self.key_fn) + 1, len(args)))

        start, stop, is_beyond = (args, args, gt) if len(args) == len(self.key_fn) else\
            (args[:-1], args[:-2] + (args[-1],), ge)

        cut_index = 0
        while cut_index < len(self.keys) and self.keys[cut_index] < start:
            cut_index += 1
        self.keys = self.keys[cut_index:]
        self.buffer = self.buffer[cut_index:]

        for item in self.iterator:
            key = tuple(fn(item) for fn in self.key_fn)
            if is_beyond(key, stop):
                self.iterator = chain([item], self.iterator)
                break
            elif key >= start:
                self.keys.append(key)
                self.buffer.append(item)

        return sorted(self.buffer)
