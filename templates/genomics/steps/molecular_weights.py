from sofia.step import Step


class MolecularWeights(Step):
    """
    Reads in a set of molecular weights. The file of molecular weights can be obtained from
    http://emboss.sourceforge.net/.
    """

    IN = ['molecular_weight_file']
    OUT = ['molecular_weight_set']

    def run(self, molecular_weight_file):
        infile = open(molecular_weight_file[0], encoding='utf-8')
        data = infile.read()
        infile.close()
        interface = {}
        for line in data.split('\n'):
            if line.strip() == '' or line[0] == '#' or line.startswith('Mol'):
                continue
            parts = line.split()
            interface[parts[0]] = {'avg': float(parts[1]), 'mono': float(parts[2])}
        yield interface
