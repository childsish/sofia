import ushuffle

def kshuffle(seq, k=2):
    return ushuffle.shuffle(seq, len(seq), k)

def randFtrs(seq, n=1000):
    tmp = calcFtrs(kshuffle(seq))
    ftrs = numpy.empty((n, len(tmp)))
    ftrs[0] = numpy.array(tmp)
    for i in xrange(1, n):
        ftrs[i] = numpy.array(calcFtrs(kshuffle(seq)))
    return numpy.mean(ftrs, 0)
