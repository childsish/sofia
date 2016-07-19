import sys

from step import Step


class Writer(Step):
    def __init__(self, entities, format=None, output=sys.stdout, **kwargs):
        self.keys = kwargs.keys()
        self.values = self.splice(*kwargs.values())
        self.entities = entities
        self.format = '\t'.join('{{{}}}'.format(entity) for entity in entities) if format is None else format
        self.format += '\n'
        self.output = output

    def run(self, txt_file):
        for values in zip(*self.values):
            self.output.write(self.format.format(**dict(zip(self.keys, values))))
        txt_file.push(StopIteration)

    def finalise(self, txt_file):
        self.output.close()
        txt_file.push(self.output.name)
        txt_file.push(StopIteration)

    def __getstate__(self):
        return self.keys, self.values, self.entities, self.format, 'stdout' if self.output is sys.stdout else self.output

    def __setstate__(self, state):
        self.keys, self.values, self.entities, self.format, self.output = state
        self.output = sys.stdout if self.output == 'stdout' else self.output
