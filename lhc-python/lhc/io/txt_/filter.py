__author__ = 'Liam Childs'


class Filter(object):
    def __init__(self, it, filters=[], constants=frozenset()):
        self.it = it
        self.filters = filters
        self.constants = constants

    def __iter__(self):
        return self

    def next(self):
        it = self.it
        filters = self.filters
        constants = self.constants

        entry = it.next()
        local_variables = entry._asdict()
        local_variables.update(constants)
        try:
            while any(eval(filter, local_variables) for filter in filters):
                entry = it.next()
                local_variables = entry._asdict()
                local_variables.update(constants)
            return entry
        except StopIteration:
            pass
        except Exception, e:
            import sys
            sys.stderr.write('error occured on line {} of {}\n'.format(it.line_no, it.fname))
            raise e
        if any(eval(filter, local_variables) for filter in filters):
            raise StopIteration
        return entry
