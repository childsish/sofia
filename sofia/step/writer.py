import sys

from step import Step, EndOfStream


class Writer(Step):
    def __init__(self, entities, format=None, output=sys.stdout):
        self.entities = entities
        self.format = '\t'.join('{{{}}}'.format(entity) for entity in entities) if format is None else format
        self.format += '\n'
        self.output = output

    def run(self, ins, outs):
        entities = self.entities
        while len(ins) > 0:
            values = ins.pop()
            if EndOfStream in values:
                outs.txt_file.push(self.output.name)
                outs.txt_file.push(EndOfStream)
                return True
            self.output.write(self.format.format(**dict(zip(entities, values))))
        return len(ins) == 0

    def __getstate__(self):
        return self.entities, self.format, 'stdout' if self.output is sys.stdout else self.output

    def __setstate__(self, state):
        self.entities, self.format, self.output = state
        self.output = sys.stdout if self.output == 'stdout' else self.output
