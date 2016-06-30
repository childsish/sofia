from lhc.binf.genetic_code import GeneticCodes

from sofia.step import Step


class GeneticCode(Step):

    IN = ['prt_file']
    OUT = ['genetic_code']

    def run(self, prt_file):
        prt_file = prt_file[0]
        yield GeneticCodes(prt_file)['Standard']

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genetic_code': set()
        }
