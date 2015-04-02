import numpy as np


def arithmetic_mean(iterable):
    return sum(iterable) / float(len(iterable))


def geometric_mean(iterable):
    return np.exp(np.mean(np.log(np.array(iterable))))
