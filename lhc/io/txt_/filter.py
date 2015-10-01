__author__ = 'Liam Childs'


class Filter(object):
    def __init__(self, it, filter, constants=frozenset()):
        self.it = it
        self.filter = filter
        self.constants = constants

    def __iter__(self):
        return self

    def next(self):
        it = self.it
        filter = self.filter
        constants = self.constants

        try:
            entry = it.next()
            local_variables = entry._asdict()
            local_variables.update(constants)
            while not eval(filter, local_variables):
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
        if not eval(filter, local_variables):
            raise StopIteration
        return entry
