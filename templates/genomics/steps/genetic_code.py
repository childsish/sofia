from lhc.binf.genetic_code import GeneticCodes

from sofia import Resource


class GeneticCode(Resource):

    EXT = ['.prt']
    FORMAT = 'prt_file'
    OUT = ['genetic_code']

    def get_interface(self, filename, gc='Standard'):
        return GeneticCodes(filename)[gc]
