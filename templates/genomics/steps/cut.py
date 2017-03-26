from lhc.io.cut import CodonUsageTable

from sofia.step import Step


class ReadCodonUsageTable(Step):

    IN = ['cut_file']
    OUT = ['codon_usage']

    def run(self, cut_file):
        yield CodonUsageTable(cut_file[0])
