class RequestedEntity(object):
    """ An entity that the user requests. """
    def __init__(self, name, getter='', header=None, attr={}, resources=frozenset()):
        self.name = name
        self.getter = '{' + getter + '}'
        self.header = name if header is None else header
        self.resources = resources
        self.attr = attr
        base = [name] if self.getter == '{}' else [name, getter]
        self.header = ':'.join(base + ['{}={}'.format(k, ','.join(v)) for k, v in sorted(attr.iteritems())])\
            if header is None else header

    def __str__(self):
        if len(self.attr) == 0:
            return self.name
        return self.name + ':' + ':'.join('{}={}'.format(k, ','.join(v)) for k, v in self.attr.iteritems())

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
