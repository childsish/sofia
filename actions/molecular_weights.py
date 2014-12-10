from sofia_.action import Resource

class MolecularWeights(Resource):
    """ Reads in a set of molecular weights.

    """
    #TODO include url where molecular weights can be obtained.

    EXT = ['.dat', '.mol']
    OUT = ['molecular_weight_set']

    def init(self):
        fname = self.getFilename()
        infile = open(fname)
        data = infile.read()
        infile.close()
        self.parser = {}
        for line in data.split('\n'):
            if line.strip() == '' or line[0] == '#' or line.startswith('Mol'):
                continue
            parts = line.split()
            self.parser[parts[0]] = {'avg': float(parts[1]), 'mono': float(parts[2])}
