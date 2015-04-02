import math
import numpy

from collections import Counter
from itertools import izip

TP = (1, 1)
TN = (0, 0)
FP = (0, 1)
FN = (1, 0)

X = 0  # True positives
Y = 1  # False positives
A = 2  # Area under curve
T = 3  # Threshold
M = 4  # Matthews correlation coefficient
B = 5  # Balanced error rate


def specificity(tp=None, tn=None, fp=None, fn=None):
    """Specificity [0, 1]
    
    This function is designed to be used with the confusion performance
    function below. If you only want to specify tp and fn, please use keyword
    arguments when calling.
    
    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    :rtype: float 
    """
    return tp / float(tp + fn)


def sensitivity(tp=None, tn=None, fp=None, fn=None):
    """Sensitivity [0, 1]
    
    This function is designed to be used with the confusion performance
    function below. If you only want to specify tp and fn, please use keyword
    arguments when calling.
    
    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    :rtype: float
    """
    return tn / float(tn + fp)


def ber(tp, tn, fp, fn):
    """Balanced Error Rate [0, 1]
    
    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    :rtype: float 
    """
    return (fp / float(tn + fp) + fn / float(fn + tp)) / 2


def mcc(tp, tn, fp, fn):
    """ Matthew's Correlation Coefficient [-1, 1]
    
    0 = you're just guessing
    
    :param int tp: number of true positives
    :param int tn: number of true negatives
    :param int fp: number of false positives
    :param int fn: number of false negatives
    :rtype: float 
    """
    if tp + fp == 0 or tp + fn == 0 or tn + fp == 0 or tn + fn == 0:
        den = 1.0
    else:
        den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / den


def mse(exp, obs):
    """Mean Squared Error
    
    :param exp: expected values
    :type exp: list of float
    :param obs: observed values
    :type obs: list of float
    """
    assert len(exp) == len(obs)
    return numpy.mean((numpy.array(exp) - numpy.array(obs)) ** 2)


def mui(x, y):
    """MUtial Information"""
    assert len(x) == len(y)
    l = len(x)
    p_x = Counter(x)
    p_y = Counter(y)
    p_xy = Counter(izip(x, y))
    return sum(p_xy[(x, y)] * math.log((p_xy[(x, y)] * l) / float(p_x[x] * p_y[y]), 2) / l
               for x, y in p_xy)


def roc(clss, vals, reverse=False):
    """ Reciever Operator Characteristic
    :param clss: known classes. 1 if positive case, -1 if the negative case
    :type class: list of boolean
    :param vals: classification probabilites etc...
    :type vals: list of real numbers
    :param bool reverse: whether the values should be sorted in reverse order
    """
    assert len(clss) == len(vals)
    global X, Y, A, T, M, B
    
    order = numpy.argsort(vals)
    if reverse:
        order = order[::-1]
    clss = numpy.array(clss)[order]
    vals = numpy.array(vals)[order]
    
    length = len(clss) + 1
    data = numpy.empty((length, 6), dtype=numpy.float32)
    data[0, X], data[0, Y], data[0, A] = 0
    data[0, T] = vals[0]
    
    for i in xrange(length-1):
        if clss[i] == 1:
            data[i+1, X] = data[i, X]
            data[i+1, Y] = data[i, Y] + 1
            data[i+1, A] = data[i, A]
        else:
            data[i+1, X] = data[i, X] + 1
            data[i+1, Y] = data[i, Y]
            data[i+1, A] = data[i, A] + data[i+1, Y]
        
        data[i+1, T] = vals[i]
    
    # Incorporate accuracy scores
    data[0, M] = 0
    for i in xrange(1, length-1):
        fp = data[i, X]
        tp = data[i, Y]
        tn = data[-1, X] - fp
        fn = data[-1, Y] - tp
        data[i, M] = mcc(tp, tn, fp, fn)
        data[i, B] = ber(tp, tn, fp, fn)
    data[-1, M] = 0
    return data


def confusion_matrix(exp, obs):
    """Create a confusion matrix
    
    In each axis of the resulting confusion matrix the negative case is
    0-index and the positive case 1-index. The labels get sorted, in a
    True/False scenario true positives will occur at (1,1). The first dimension
    (rows) of the resulting matrix is the expected class and the second
    dimension (columns) is the observed class.
    
    :param exp: expected values
    :type exp: list of float
    :param obs: observed values
    :type obs: list of float
    :rtype: tuple of square matrix and sorted labels
    """
    assert len(exp) == len(obs)
    # Expected in the first dimension (0;rows), observed in the second (1;cols)
    lbls = sorted(set(exp))
    res = numpy.zeros(shape=(len(lbls), len(lbls)))
    for i in xrange(len(exp)):
        res[lbls.index(exp[i]), lbls.index(obs[i])] += 1
    return res, lbls


def confusion_performance(mat, fn):
    """Apply a performance function to a confusion matrix
    
    :param mat: confusion matrix
    :type mat: square matrix
    :param function fn: performance function
    """
    if mat.shape[0] != mat.shape[1] or mat.shape < (2, 2):
        raise TypeError('{} is not a confusion matrix'.format(mat))
    elif mat.shape == (2, 2):
        return fn(mat[TP], mat[TN], mat[FP], mat[FN])
    res = numpy.empty(mat.shape[0])
    for i in xrange(len(res)):
        res[i] = fn(mat[i, i],                                   # TP
                    sum(mat) - sum(mat[:, i]) - sum(mat[i, :]),  # TN
                    sum(mat[:, i]) - mat[i, i],                  # FP
                    sum(mat[i, :]) - mat[i, i])                  # FN
    return res
