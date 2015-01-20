from collections import namedtuple

GeneRif = namedtuple('GeneRif', ('gene_id', 'pubmed_id', 'description'))

def iterGeneRif(fname):
    infile = open(fname)
    for line in infile:
        parts = line.strip().split('\t')
        yield GeneRif(parts[1], parts[2], parts[4])
    infile.close()
