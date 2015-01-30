class RequestedEntity(object):
    """ An entity that the user requests. """
    def __init__(self, name, getter='', header=None, attr={}, resources=frozenset()):
        self.name = name
        self.getter = '{' + getter + '}'
        self.header = name if header is None else header
        self.resources = resources
        self.attr = attr
        base = [name] if self.getter == '{}' else [name, getter]
        self.header = ':'.join(base + ['{}={}'.format(k, v) for k, v in sorted(attr.iteritems())])\
            if header is None else header

    def __str__(self):
        return self.header

    def __eq__(self, other):
        return str(self) == str(other)
    
    def format(self, entity):
        try:
            if isinstance(entity, (set, list)):
                return ','.join(self.getter.format(e) for e in entity)
            return '' if entity is None else self.getter.format(entity)
        except KeyError:
            pass
        return ''
