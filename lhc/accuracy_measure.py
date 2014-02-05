import numpy
import math

X = 0 # True positives
Y = 1 # False positives
A = 2 # Area under curve
T = 3 # Threshold
M = 4 # Matthews correlation coefficient

def roc(clss, vals):
    """ clss: boolean. True if positive case, False if the negative case
    vals: list of real numbers.
    """
    global X, Y, A, T, M
    
    order = numpy.argsort(vals)
    clss = numpy.array(clss)[order]
    vals = numpy.array(vals)[order]
    
    length = len(clss) + 1
    data = numpy.empty( (length, 5) , dtype=numpy.float32)
    data[0, X] = 0; data[0, Y] = 0; data[0, A] = 0
    data[0, T] = vals[0]
    
    for i in xrange(length-1):
        if clss[i]:
            data[i+1, X] = data[i, X]
            data[i+1, Y] = data[i, Y] + 1
            data[i+1, A] = data[i, A]
        else:
            data[i+1, X] = data[i, X] + 1
            data[i+1, Y] = data[i, Y]
            data[i+1, A] = data[i, A] + data[i+1, Y]
        
        data[i+1, T] = vals[i]
    
    # Incorporate MCC score
    data[0, M] = 0
    for i in xrange(1, length-1):
        fp = data[i,X]
        tp = data[i,Y]
        tn = data[-1,X] - fp
        fn = data[-1,Y] - tp
        if tp + fp == 0 or tp + fn == 0 or tn + fp == 0 or tn + fn == 0:
            den = 1
        else:
            den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        data[i,M] = (tp * tn - fp * fn) / den
    data[-1, M] = 0
    return data

def mse(exp, obs):
    return numpy.mean((numpy.array(exp) - numpy.array(obs)) ** 2)

def confusion(exp, obs):
    # Observed in the first dimension, expected in the second
    lbls = sorted(set(exp))
    res = numpy.zeros(shape=(len(lbls), len(lbls)))
    for i in xrange(len(exp)):
        res[lbls.index(exp[i]),lbls.index(obs[i])] += 1
    return res

def step_matrix(mat, fn):
    res = numpy.empty(mat.shape[0])
    for i in xrange(len(res)):
        sub_mat = numpy.empty((2,2))
        sub_mat[1,1] = mat[i,i]
        sub_mat[1,0] = sum(mat[:,i]) - mat[i,i]
        sub_mat[0,1] = sum(mat[i,:]) - mat[i,i]
        sub_mat[0,0] = sum(mat) - sum(mat[:,i]) - sum(mat[i,:])
        res[i] = fn(sub_mat)
    return res

def mcc(mat, pve=1):
    """ Matthew's Correlation Coefficient [-1, 1]. Calculated from a
            confusion matrix.
        """
    if mat.shape == (2,2):
        nve = 1 - pve
        tp = mat[pve,pve]
        fn = mat[pve,nve]
        fp = mat[nve,pve]
        tn = mat[nve,nve]
        if tp + fp == 0 or tp + fn == 0 or tn + fp == 0 or tn + fn == 0:
            den = 1
        else:
            den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        return (tp * tn - fp * fn) / den
    return step_matrix(mat, mcc)

def ber(mat, pve=1):
    """ Balanced ERror rate [0, 1]"""
    if mat.shape == (2,2):
        nve = 1 - pve
        tp = mat[pve,pve]
        fn = mat[pve,nve]
        fp = mat[nve,pve]
        tn = mat[nve,nve]
        return 0.5 * (fp / (tn + fp) + fn / (fn + tp))
    return step_matrix(mat, ber)

def mui(X, Y):
    """ MUtial Information """
    assert len(X) == len(Y)
    
    # Calculate the joint and marginal probabilities
    l = len(X)
    pX = {}
    pY = {}
    pXY = {}
    for i in xrange(l):
        pX.setdefault(X[i], 0)
        pX[X[i]] += 1
        pY.setdefault(Y[i], 0)
        pY[Y[i]] += 1
        pXY.setdefault((X[i], Y[i]), 0)
        pXY[(X[i], Y[i])] += 1
    for x in pX:
        pX[x] = pX[x] / float(l)
    for y in pY:
        pY[y] = pY[y] / float(l)
    for xy in pXY:
        pXY[xy] = pXY[xy] / float(l)
    
    ttl = 0
    for x, y in pXY:
        ttl += pXY[(x, y)] * math.log(pXY[(x, y)] / (pX[x] * pY[y]), 2)
    return ttl
