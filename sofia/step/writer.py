import sys

from step import Step


class Writer(Step):
    def __init__(self, entities, format=None, output=sys.stdout):
        self.entities = entities
        self.format = '\t'.join('{{{}}}'.format(entity) for entity in entities) if format is None else format
        self.output = output

    def run(self, **kwargs):
        self.output.write(self.format.format(**kwargs))
