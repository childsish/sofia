class StreamSet(object):
    def __init__(self, entities, streams):
        self.__dict__ = dict(zip(entities, streams))

    def __len__(self):
        return len(next(iter(self.values())))

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self):
        return [in_.pop() for in_ in self.values()]
