'''
Created on 06/08/2013

@author: Liam Childs
'''

from bisect import bisect_left, bisect_right, insort

class IntervalList(object):

    def __init__(self, ivls=None, length=None):
        self.ivls = sorted(ivls)
        self.length = length
    
    def __len__(self):
        return len(self.ivls)
    
    def insert(self, ivl):
        insort(self.ivls, ivl)
    
    def query(self, ivl):
        fr = bisect_left(self.ivls, ivl.start)
        while fr < len(self) and self.ivls[fr].stop <= ivl.start:
            fr += 1
        to = bisect_right(self.ivls, ivl.stop)
        while self.ivls[to].start < ivl.stop:
            to += 1
        return self.ivls[fr:to]