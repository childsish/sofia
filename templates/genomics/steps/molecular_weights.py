from sofia.step import Step, EndOfStream


class MolecularWeights(Step):
    """
    Reads in a set of molecular weights. The file of molecular weights can be obtained from
    http://emboss.sourceforge.net/.
    """

    IN = ['molecular_weight_file']
    OUT = ['molecular_weight_set']

    def run(self, ins, outs):
        while len(ins) > 0:
            molecular_weight_file = ins.molecular_weight_file.pop()
            if molecular_weight_file is EndOfStream:
                outs.molecular_weight_set.push(EndOfStream)
                return True

            molecular_weight_set = self.get_molecular_weight_set(molecular_weight_file)
            if not outs.molecular_weight_set.push(molecular_weight_set):
                break
        return len(ins) == 0

    def get_molecular_weight_set(self, filename):
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
