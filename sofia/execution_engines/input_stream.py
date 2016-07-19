from collections import defaultdict


class InputStream(object):

    __slots__ = ('index', 'input', 'threshold', 'chunks', 'finished')

    def __init__(self, threshold, input=None):
        self.index = 0
        self.input = [] if input is None else input
        self.threshold = threshold
        self.chunks = defaultdict(list)
        self.finished = False

    def __iter__(self):
        return iter(self.input)

    def __len__(self):
        return len(self.input)

    def is_readable(self):
        return len(self.input) > 0

    def is_writable(self):
        return len(self.input) < self.threshold

    def is_finished(self):
        return len(self.input) == 0 and self.finished

    def peek(self):
        return self.input[0]

    def pop(self):
        return self.input.pop(0)

    def read(self):
        return self.input[:]

    def consume(self, n=None):
        if n is None:
            n = len(self.input)
        res = InputStream(self.threshold, self.input[:n])
        del self.input[:n]
        return res

    def write(self, entities, index):
        self.chunks[index].extend(entities)
        while self.index in self.chunks:
            index = self.index
            self.input.extend(entity for entity in self.chunks[index] if entity is not StopIteration)
            if self.chunks[index][-1] is StopIteration:
                self.index += 1
            del self.chunks[index]

    def __getstate__(self):
        return self.index, self.input, self.threshold, self.chunks, self.finished

    def __setstate__(self, state):
        self.index, self.input, self.threshold, self.chunks, self.finished = state
