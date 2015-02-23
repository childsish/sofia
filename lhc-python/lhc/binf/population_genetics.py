import numpy as np

def kinship(dataset):
    '''
    
    :param dataset: the genotypes to calculate the distance between
    :type dataset: NetCDF4 matrix
    '''
    n_gen = len(dataset.dimensions['gen'])
    vars = dataset.variables['vars']
    res = np.zeros((n_gen, n_gen), dtype=np.int32)
    for i in xrange(n_gen):
        for j in xrange(i + 1, n_gen):
            print i, j
            d = np.sum(vars[i,:] != vars[j,:])
            res[i,j] = d
            res[j,i] = d
    return res
