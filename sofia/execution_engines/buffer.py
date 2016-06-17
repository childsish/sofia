from itertools import repeat


class Buffer(object):
    def __init__(self, keys, n=None):
        self.frozen = set()
        self.keys = keys
        self.n = n
        self.items = {key: [] for key in keys}

    def __contains__(self, item):
        return item in self.keys

    def is_readable(self):
        return min(len(v) for v in self.items.itervalues()) > 0

    def is_writable(self, keys):
        return all(len(self.items[key]) < self.n and key not in self.frozen for key in keys)

    def read(self):
        inputs = []
        lengths = []
        for key in self.keys:
            input = self.items[key][:self.n]
            inputs.append(input)
            lengths.append(len(input))
            self.items[key] = self.items[key][self.n:]
        if len(set(lengths) - {1}) > 1:
            raise ValueError('unable to handle inputs of different lengths')
        n = max(lengths)
        if n > 1:
            for i in xrange(len(inputs)):
                if lengths[i] == 1:
                    inputs[i] = repeat(inputs[i][0], n)
                    self.frozen.add(self.keys[i])
                elif self.keys[i] in self.frozen:
                    self.frozen.remove(self.keys[i])
        else:
            self.frozen = set()
        return inputs

    def write(self, key, values):
        self.items[key].extend(values)
