import sys

from sofia.step.step import Step


class Writer(Step):
    def __init__(self, entities, format=None, output=sys.stdout):
        self.entities = entities
        self.format = '\t'.join('{{{}}}'.format(entity) for entity in entities) if format is None else format
        self.format += '\n'
        self.output = output

    def run(self, **kwargs):
        keys = kwargs.keys()
        for values in zip(*kwargs.values()):
            self.output.write(self.format.format(**dict(zip(keys, values))))
        for k in kwargs:
            del kwargs[k][:]
        return
        yield  # allows the generator to return nothing

    def finalise(self):
        yield self.output

    def __getstate__(self):
        return self.entities, self.format, 'stdout' if self.output is sys.stdout else self.output

    def __setstate__(self, state):
        self.entities = state[0]
        self.format = state[1]
        self.output = sys.stdout if state[2] == 'stdout' else state[2]
