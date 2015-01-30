class RequestedEntity(object):
    """ An entity that the user requests. """
    def __init__(self, name, getter='', attr={}, resources=frozenset()):
        self.name = name
        self.getter = '{' + getter + '}'
        self.resources = resources
        self.attr = attr

    def __str__(self):
        res = [self.name]
        if len(self.attr) > 0:
            res.append(','.join('{}={}'.format(k, ','.join(v)) for k, v in sorted(self.attr.iteritems())))
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)
    
    def format(self, entity):
        if isinstance(entity, (set, list)):
            return ','.join(self.getter.format(e) for e in entity)
        return '' if entity is None else self.getter.format(entity)
