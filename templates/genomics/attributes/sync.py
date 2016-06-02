from operator import or_
from sofia.resolvers import AttributeResolver


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'sync'

    def resolve_out(self, ins):
        values = reduce(or_, ins.itervalues())
        if len(values) > 1:
            raise ValueError('Unable to resolve sync stream')
        return {key: values for key in self.step.outs}
