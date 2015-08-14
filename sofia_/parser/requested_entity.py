class RequestedEntity(object):
    """ An entity that the user requests. """
    def __init__(self, name, getter='', header=None, attr={}, resources=frozenset()):
        self.name = name
        self.getter = '{' + getter + '}'
        self.resources = resources
        self.attr = attr
        base = [name] if self.getter == '{}' else [name, getter]

        self.header = header
        if header is None:
            header = [self.name]
            header.extend('{}={}'.format(k, v) for k, v in self.attr.iteritems())
            self.header = ':'.join(header)

    def __str__(self):
        res = [self.name]
        res.extend('{}={}'.format(k, v) for k, v in self.attr.iteritems())
        return ':'.join(res)

    def __eq__(self, other):
        return str(self) == str(other)
    
    def format(self, entity):
        try:
            if isinstance(entity, (set, list)):
                return ','.join(self.getter.format(e) for e in entity)
            return '' if entity is None else self.getter.format(entity)
        except Exception, e:
            import sys
            sys.stderr.write('Error formatting entity {}.\n'.format(self.name))
            sys.stderr.write('Format string: {}.\n'.format(self.getter))
            sys.stderr.write('Entity: {}.\n'.format(entity))
            #raise e
        return ''
