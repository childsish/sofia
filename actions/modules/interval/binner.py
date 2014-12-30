class IntervalBinner(object):
    def __init__(self, minbin=2, maxbin=8):
        self.minbin = minbin
        self.maxbin = maxbin
    
    def get_bin(self, start, stop):
        for i in range(self.minbin, self.maxbin):
            bin_level = 10 ** i
            if int(start / bin_level) == int(stop / bin_level):
                return int(i * 10 ** self.maxbin + int(start / bin_level))
        return int(self.maxbin * 10 ** self.maxbin)

    def get_overlapping_bins(self, start, stop):
        res = []
        big_bin = int(self.maxbin * 10 ** self.maxbin)
        for i in range(self.minbin, self.maxbin + 1):
            bin_level = 10 ** i
            fr = int(i * 10 ** self.maxbin + int(start / bin_level))
            to = int(i * 10 ** self.maxbin + int(stop / bin_level))
            res.append((fr, to))
        res.append((big_bin, big_bin))
        return res
