from sofia_.action import Resource

from modules.binf.genetic_code import GeneticCodes


class GeneticCode(Resource):

    EXT = ['.gc']
    OUT = ['genetic_code']
    DEFAULT = 'gc.prt'

    def init(self, gc='Standard'):
        fname = self.get_filename()
        self.parser = GeneticCodes(fname)[gc]
