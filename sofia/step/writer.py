import sys

from sofia.step.step import Step


class Writer(Step):
    def __init__(self, entities, output=sys.stdout):
        self.entities = entities
        self.output = output

    def run(self, **kwargs):
        for values in zip(*[kwargs[entity.name] for entity in self.entities]):
            res = [entity.format(value) for entity, value in zip(self.entities, values)]
            self.output.write('\t'.join(res))
            self.output.write('\n')
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
