from lhc.io.cut import CodonUsageTable

from sofia.step import Step


class ReadCodonUsageTable(Step):

    EXT = {'.cut'}
    FORMAT = 'cut_file'
    OUT = ['codon_usage']

    def get_interface(self, filename):
        self.parser = CodonUsageTable(filename)
