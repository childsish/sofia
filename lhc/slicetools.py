'''
Created on 06/08/2013

@author: Liam Childs
'''

def overlaps(a, b, length=None):
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start <= b.start and a.stop > b.start or\
        b.start < a.stop and b.stop >= a.stop

def contains(a, b, length=None):
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start <= b.start and a.stop >= b.stop

def getAbsPos(self, ivl, pos, length=None):
    ivl = normalise(ivl, length)
    return ivl.start + pos

def getRelPos(self, ivl, pos, length=None):
    ivl = normalise(ivl, length)
    if pos < ivl.start or pos >= ivl.stop:
        err = 'Absolute position %d is not contained within %s'
        raise IndexError(err%(pos, ivl))
    return pos - ivl.start

def normalise(ivl, length=None):
    return slice(ivl.start if ivl.start >= 0 else length + ivl.start,
        ivl.stop if ivl.stop >= 0 else length + ivl.stop, ivl.step)