from lhc.io.cut import CodonUsageTable

from sofia.step import Resource


class ReadCodonUsageTable(Resource):

    EXT = {'.cut'}
    FORMAT = 'cut_file'
    OUT = ['codon_usage']

    def get_interface(self, filename):
        self.parser = CodonUsageTable(filename)
