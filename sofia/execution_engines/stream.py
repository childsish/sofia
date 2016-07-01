class InputStream(object):
    __slots__ = ('input',)

    def __init__(self, input):
        self.input = input

    def peek(self):
        return self.input[0]

    def pop(self):
        return self.input.pop(0)

    def splice(self):
        res = self.input[:]
        del self.input[:]
        return res

    def __getstate__(self):
        return self.input

    def __setstate__(self, state):
        self.input = state[0]


class OutputStream(object):
    __slots__ = ('threshold', 'output')

    def __init__(self, output, threshold):
        self.output = output
        self.threshold = threshold

    def push(self, entity):
        self.output.push(entity)
        return len(self.output) >= self.threshold

    def __getstate__(self):
        return self.output, self.threshold

    def __setstate__(self, state):
        self.output = state[0]
        self.threshold = state[1]
