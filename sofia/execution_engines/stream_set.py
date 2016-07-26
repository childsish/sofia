class StreamSet(object):
    def __init__(self, entities, streams):
        self.__dict__ = dict(zip(entities, streams))

    def __len__(self):
        return len(self.itervalues().next())

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def iteritems(self):
        return self.__dict__.iteritems()

    def pop(self):
        return [in_.pop() for in_ in self.itervalues()]
