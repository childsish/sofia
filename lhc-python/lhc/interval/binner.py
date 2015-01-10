class IntervalBinner(object):
    
    def __init__(self, minbin=2, maxbin=7):
        self.minbin = minbin
        self.maxbin = maxbin
    
    def getBin(self, ivl):
        for i in range(self.minbin, self.maxbin + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.stop / binLevel):
                return int(i * 10 ** (self.maxbin + 1) + int(ivl.start / binLevel))
        return int((self.maxbin + 1) * 10 ** (self.maxbin + 1))

    def getOverlappingBins(self, ivl):
        res = []
        bigBin = int((self.maxbin + 1) * 10 ** (self.maxbin + 1))
        for i in range(self.minbin, self.maxbin + 1):
            binLevel = 10 ** i
            fr = int(i * 10 ** (self.maxbin + 1) + int(ivl.start / binLevel))
            to = int(i * 10 ** (self.maxbin + 1) + int(ivl.stop / binLevel))
            res.append((fr, to))
        res.append((bigBin, bigBin))
        return res

