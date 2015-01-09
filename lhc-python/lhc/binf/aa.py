from pkg_resources import resource_string

def readMolWeight(fname=None):
    if fname is None:
        data = resource_string(__name__, '../data/Emolwt.dat')
    else:
        infile = open(fname)
        data = infile.read()
        infile.close()
    res = {}
    for line in data.split('\n'):
        if line.strip() == '' or line[0] == '#' or line.startswith('Mol'):
            continue
        parts = line.split()
        res[parts[0]] = {'avg': float(parts[1]), 'mono': float(parts[2])}
    return res
