from sofia_.step import Resource

from lhc.io.cut import CodonUsageTable


class ReadCodonUsageTable(Resource):

    EXT = {'.cut'}
    FORMAT = 'cut_file'
    OUT = ['codon_usage']

    def get_interface(self, filename):
        self.parser = CodonUsageTable(filename)
