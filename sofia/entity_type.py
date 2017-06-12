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
        res = [self.name if self.name == self.alias else '{} ({})'.format(self.alias, self.name)]
        res.extend('{}={}'.format(k, str(v) if isinstance(v, str) else ','.join(v)) for k, v in sorted(self.attributes.items()))
        return '\\n'.join(res)

    def __hash__(self):
        attributes = tuple((key, frozenset(values)) for key, values in self.attributes.items())
        return hash(self.name) + hash(attributes)

    def __eq__(self, other):
        return self.name == other.name and self.attributes == other.attributes

    def __lt__(self, other):
        return str(self) < str(other)

    def format(self, entity):
        try:
            if isinstance(entity, (set, list)):
                return ','.join(self.format_string.format(e) for e in entity)
            return '' if entity is None else self.format_string.format(entity)
        except Exception as e:
            import sys
            sys.stderr.write('Error formatting entity {}.\n'.format(self.name))
            sys.stderr.write('Format string: {}.\n'.format(self.format_string))
            sys.stderr.write('Entity: {}.\n'.format(entity))
            sys.stderr.write('Error: {}\n'.format(e))
            #raise e
        return ''
