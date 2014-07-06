import numpy as np

def gmean(seq):
    """ Calculate the geometric mean. """
    return np.exp(np.mean(np.log(np.array(seq))))