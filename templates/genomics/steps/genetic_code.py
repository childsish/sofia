from lhc.binf.genetic_code import GeneticCodes

from sofia.step import Step


class GeneticCode(Step):

    IN = ['prt_file']
    OUT = ['genetic_code']

    def run(self, prt_file):
        yield GeneticCodes(prt_file)['Standard']
