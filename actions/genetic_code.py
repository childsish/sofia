from sofia_.action import Resource

from lhc.binf.genetic_code import GeneticCodes

class GeneticCode(Resource):

    EXT = ['.gc']
    OUT = ['genetic_code']

    def init(self, gc=None):
        gc = 0 if gc is None else gc
        fname = self.getFilename()
        self.parser = GeneticCodes(fname)[gc]
