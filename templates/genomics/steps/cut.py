from lhc.io.cut import CodonUsageTable
from sofia.step import Step, EndOfStream


class ReadCodonUsageTable(Step):

    IN = ['cut_file']
    OUT = ['codon_usage']

    def run(self, ins, outs):
        while len(ins) > 0:
            cut_file = ins.cut_file.pop()
            if cut_file is EndOfStream:
                outs.codon_usage.push(EndOfStream)
                return True
            codon_usage = None if cut_file is None else CodonUsageTable(cut_file)
            if not outs.codon_usage.push(codon_usage):
                break
        return len(ins) == 0
