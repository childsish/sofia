from sofia_.step import Resource

from lhc.binf.genetic_code import GeneticCodes


class GeneticCode(Resource):

    EXT = ['.gc']
    OUT = ['genetic_code']
    DEFAULT = 'gc.prt'

    def get_interface(self, filename, gc='Standard'):
        return GeneticCodes(filename)[gc]
