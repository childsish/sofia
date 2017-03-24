from sofia.resolvers import AttributeResolver


class ChromosomeIdResolver(AttributeResolver):

    ATTRIBUTE = 'sync'

    def resolve_out(self, ins):
        values = set()
        for value in ins.values():
            values.update(value)
        if len(values) > 1:
            raise ValueError('Unable to resolve sync stream')
        return {key: values for key in self.step.outs}
