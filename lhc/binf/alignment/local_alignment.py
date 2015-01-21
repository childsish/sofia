import numpy as np

class LocalAlignment(object):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
        self.scores = np.zeros((len(s1) + 1, len(s2) + 1))
        self.pointers = np.zeros((len(s1) + 1, len(s2) + 1))
        self._start = None
        self.stop = (0, 0)
    
    def __str__(self):
        s1 = self.s1
        s2 = self.s2
        a1 = []
        a2 = []
        a = []
        i, j = self.stop
        while self.scores[i, j] > 0:
            if self.pointers[i, j] == 1:
                a1.append('_')
                a2.append(s2[j - 1])
                a.append(' ')
                j -= 1
            elif self.pointers[i, j] == 2:
                a1.append(s1[i - 1])
                a2.append('_')
                a.append(' ')
                i -= 1
            elif self.pointers[i, j] == 3:
                a1.append(s1[i - 1])
                a2.append(s2[j - 1])
                a.append('|' if s1[i - 1] == s2[j - 1] else '.')
                i -= 1
                j -= 1
        return '%s\n%s\n%s' %\
            (''.join(reversed(a1)), ''.join(reversed(a)), ''.join(reversed(a2)))
    
    @property
    def start(self):
        if self._start is None:
            self._start = self._trace_alignment()
        return self._start

    @property
    def score(self):
        return self.scores[self.stop]
    
    def get_score(self, i, j):
        return self.scores[i, j]
    
    def set_score(self, i, j, score):
        self.scores[i, j] = score
        if score > self.scores[self.stop]:
            self.stop = (i, j)
    
    def get_pointer(self, i, j):
        return self.pointers[i, j]

    def set_pointer(self, i, j, pointer):
        self.pointers[i, j] = pointer

    def _trace_alignment(self):
        i, j = self.stop
        while self.scores[i, j] > 0:
            if self.pointers[i, j] in (2, 3):
                i -= 1
            if self.pointers[i, j] in (1, 3):
                j -= 1
        return i - 1, j - 1
