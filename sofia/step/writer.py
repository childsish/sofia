import sys

from step import Step


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
