from lhc.io.csv_ import CsvIterator, CsvSet
from resource import Target, Resource, Step


class TxtIterator(Target):

    EXT = set()
    FORMAT = None

    def init(self, entry, skip=0):
        self.parser = CsvIterator(self.get_filename(), entry, skip=skip)


class TxtSet(Resource):

    EXT = set()
    FORMAT = None

    def init(self, entry, index, key, skip=0):
        self.parser = CsvSet(CsvIterator(self.get_filename(), entry, skip=skip), index(), key)


class TxtAccessor(Step):
    def init(self, set_name, key_name):
        self.set_name = set_name
        self.key_name = key_name

    def calculate(self, **kwargs):
        return kwargs[self.set_name][kwargs[self.key_name]]
