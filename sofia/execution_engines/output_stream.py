from collections import deque
from sofia.step import EndOfStream


class OutputStream(object):

    __slots__ = ('has_ended', 'output', 'threshold', 'consumers')

    def __init__(self, threshold, consumers):
        self.has_ended = False
        self.output = deque()
        self.threshold = threshold
        self.consumers = consumers

    def is_readable(self):
        return len(self.output) > 0

    def is_writable(self):
        return len(self.output) < self.threshold and not self.has_ended

    def is_done(self):
        return len(self.output) > 0 and self.output[-1] is EndOfStream

    def consume(self):
        res = list(self.output)
        self.output.clear()
        return res

    def push(self, *entities):
        self.output.extend(entities)
        if entities[-1] is EndOfStream:
            self.has_ended = True
        return self.is_writable()

    def __getstate__(self):
        return self.has_ended, self.output, self.threshold, self.consumers

    def __setstate__(self, state):
        self.has_ended, self.output, self.threshold, self.consumers = state
