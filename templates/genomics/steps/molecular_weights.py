from sofia import Resource


class MolecularWeights(Resource):
    """
    Reads in a set of molecular weights. The file of molecular weights can be obtained from
    http://emboss.sourceforge.net/.
    """

    EXT = ['.dat', '.mol']
    OUT = ['molecular_weight_set']
    DEFAULT = 'Emolwt.dat'
    FORMAT = 'molecular_weight_file'

    def get_interface(self, filename):
        infile = open(filename)
        data = infile.read()
        infile.close()
        interface = {}
        for line in data.split('\n'):
            if line.strip() == '' or line[0] == '#' or line.startswith('Mol'):
                continue
            parts = line.split()
            interface[parts[0]] = {'avg': float(parts[1]), 'mono': float(parts[2])}
        return interface
