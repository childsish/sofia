from sofia_.step import Resource

from lhc.binf.genetic_code import GeneticCodes


class GeneticCode(Resource):

    EXT = ['.gc']
    FORMAT = 'genetic_code_file'
    OUT = ['genetic_code']

    def get_interface(self, filename, gc='Standard'):
        return GeneticCodes(filename)[gc]
