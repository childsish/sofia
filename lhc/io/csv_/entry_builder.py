class EntryBuilder(object):
    def __init__(self, type, builders=[], columns=[]):
        self.type = type
        self.builders = builders
        self.columns = columns

    def __call__(self, parts):
        tmp = [builder(parts) for builder in self.builders] + [parts[column] for column in self.columns]
        return self.type(*[builder(parts) for builder in self.builders] + [parts[column] for column in self.columns])
