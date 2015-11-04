__author__ = 'Liam Childs'


class Filter(object):
    def __init__(self, iterator, filter, formatter, constants=frozenset()):
        """

        :param iterator: stream of classified strings
        :param filter: filter to apply. pass means keep
        :param formatter: parse each line using this formatter
        :param constants: added to filter evaluation
        :return:
        """
        self.iterator = iterator
        self.filter = filter
        self.formatter = formatter
        self.constants = constants

    def __iter__(self):
        filter = self.filter
        formatter = self.formatter
        constants = self.constants

        for line in self.iterator:
            if line.type != 'line':
                yield line.value
            local_variables = formatter(line.value)._asdict()
            local_variables.update(constants)
            if eval(filter, local_variables):
                yield line.value
