class EntityType(object):
    """
    An "entity" represents data that is processed by steps in a workflow. They can be considered nouns and the step can
    be considered verbs.
    """
    def __init__(self, name, attributes=None, alias=None, format_string=''):
        self.name = name
        self.attributes = {} if attributes is None else attributes
        self.alias = name if alias is None else alias
        self.format_string = '{' + format_string + '}'

    def __str__(self):
        res = [self.alias]
        res.extend('{}={}'.format(k, str(v) if isinstance(v, basestring) else ','.join(v)) for k, v in sorted(self.attributes.iteritems()))
        return '\\n'.join(res)

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def format(self, entity):
        try:
            if isinstance(entity, (set, list)):
                return ','.join(self.format_string.format(e) for e in entity)
            return '' if entity is None else self.format_string.format(entity)
        except Exception, e:
            import sys
            sys.stderr.write('Error formatting entity {}.\n'.format(self.name))
            sys.stderr.write('Format string: {}.\n'.format(self.format_string))
            sys.stderr.write('Entity: {}.\n'.format(entity))
            #raise e
        return ''
