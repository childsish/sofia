__author__ = 'Liam Childs'


class Entity(object):
    """ An "entity" represents data that is processed by steps in a workflow.
        They can be considered nouns and the step can be considered verbs.
    """
    def __init__(self, name, resources=frozenset(), attr=None, alias=None, getter=''):
        self.name = name
        self.resources = resources
        self.attr = {} if attr is None else attr
        self.alias = name if alias is None else alias
        self.getter = '{' + getter + '}'

    def __str__(self):
        res = [self.alias, 'resource={}'.format(','.join(sorted(self.resources)))]
        res.extend('{}={}'.format(k, str(v)) for k, v in sorted(self.attr.iteritems()))
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
