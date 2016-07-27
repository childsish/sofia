from lhc.binf.genetic_code import GeneticCodes
from sofia.step import Step, EndOfStream


class GeneticCode(Step):

    IN = ['prt_file']
    OUT = ['genetic_code']

    def run(self, ins, outs):
        while len(ins) > 0:
            prt_file = ins.prt_file.pop()
            if prt_file is EndOfStream:
                outs.genetic_code.push(EndOfStream)
                return True

            genetic_code = GeneticCodes(prt_file)['Standard']
            if not outs.genetic_code.push(genetic_code):
                break
        return len(ins) == 0

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
