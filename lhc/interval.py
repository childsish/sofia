from functools import total_ordering

@total_ordering
class interval(object):
    def __init__(self, start, stop):
        self.start, self.stop = sorted((start, stop))

    def __str__(self):
        return '[%d..%d)'%(self.start, self.stop)
    
    def __hash__(self):
        return hash((self.start, self.stop))
    
    def __lt__(self, other):
        if self.start < other.start:
            return True
        elif self.start > other.start:
            return False
        return self.stop < other.stop
    
    def __eq__(self, other):
        return self.start == other.start and self.stop == other.stop

    def __len__(self):
        return self.stop - self.start

    def __contains__(self, pos):
        return self.start <= pos and pos < self.stop

    def __sub__(self, other):
        # No overlap
        if self.start > other.stop or other.start > self.stop:
            return [None, self]
    
        res = [None, None]
        if self.start < other.start:
            res[0] = interval(self.start, other.start)
        if other.stop < self.stop:
            res[1] = interval(other.stop, self.stop)
        return res

    def __and__(self, other):
        # No overlap
        if self.start > other.stop or other.start > self.stop:
            return None
    
        res = interval(self.start, self.stop)
        if self.start < other.start:
            res.start = other.start
        if other.stop < self.stop:
            res.stop = other.stop
        return res

    def __or__(self, other):
        # No overlap
        if self.start > other.stop or other.start > self.stop:
            return [self, other]
        
        ivl = interval(other.start, other.stop)
        res = [ivl, None]
        if self.start < other.start:
            res[0].start = self.start
        if other.stop < self.stop:
            res[0].stop = self.stop
        return res
    
    def getAbsPos(self, pos):
        return self.start + pos
        
    def getRelPos(self, pos):
        if pos < self.start or pos >= self.stop:
            err = 'Absolute position %d is not contained within %s'
            raise IndexError(err%(pos, self))
        return pos - self.start