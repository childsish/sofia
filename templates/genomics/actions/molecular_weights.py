from sofia_.action import Resource


class MolecularWeights(Resource):
    """
    Reads in a set of molecular weights. The file of molecular weights can be obtained from
    http://emboss.sourceforge.net/.
    """

    EXT = ['.dat', '.mol']
    OUT = ['molecular_weight_set']
    DEFAULT = 'Emolwt.dat'

    def init(self):
        fname = self.get_filename()
        infile = open(fname)
        data = infile.read()
        infile.close()
        self.parser = {}
        for line in data.split('\n'):
            if line.strip() == '' or line[0] == '#' or line.startswith('Mol'):
                continue
            parts = line.split()
            self.parser[parts[0]] = {'avg': float(parts[1]), 'mono': float(parts[2])}
