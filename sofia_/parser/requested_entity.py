class RequestedEntity(object):
    """ An entity that the user requests. """
    def __init__(self, name, attr={}, resources=frozenset()):
        self.name = name
        self.resources = resources
        self.attr = attr

    def __str__(self):
        res = [self.name]
        if len(self.attr) > 0:
            res.append(','.join('{}={}'.format(e, e) for e in sorted(self.param.iteritems())))
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)
