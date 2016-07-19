from collections import deque


class OutputStream(object):

    __slots__ = ('output', 'threshold', 'consumers')

    def __init__(self, threshold, consumers):
        self.output = deque()
        self.threshold = threshold
        self.consumers = consumers

    def is_readable(self):
        return len(self.output) > 0

    def is_writable(self):
        return len(self.output) < self.threshold

    def is_stopped(self):
        return len(self.output) > 0 and self.output[-1] is StopIteration

    def consume(self):
        res = list(self.output)
        self.output.clear()
        return res

    def push(self, entity):
        self.output.append(entity)
        return self.is_writable() and entity is not StopIteration

    def __getstate__(self):
        return self.output, self.threshold, self.consumers

    def __setstate__(self, state):
        self.output, self.threshold, self.consumers = state
