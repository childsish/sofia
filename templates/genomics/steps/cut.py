from sofia_.step import Resource

from lhc.io.cut import CodonUsageTable


class ReadCodonUsageTable(Resource):

    EXT = ['.cut']
    OUT = ['codon_usage']

    def init(self):
        self.parser = CodonUsageTable(self.get_filename())
