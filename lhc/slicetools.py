"""Tools that treat slices like intervals."""

def overlaps(a, b, length=None):
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start < b.stop and b.start < a.stop

def contains(a, b, length=None):
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start <= b.start and a.stop >= b.stop

def getAbsPos(ivl, pos, length=None):
    ivl = normalise(ivl, length)
    if pos < 0 or pos >= ivl.stop - ivl.start:
        err = 'Relative position %d is not contained within %s'
        raise IndexError(err)
    return ivl.start + pos

def getRelPos(ivl, pos, length=None):
    ivl = normalise(ivl, length)
    if pos < ivl.start or pos >= ivl.stop:
        err = 'Absolute position %d is not contained within %s'
        raise IndexError(err%(pos, ivl))
    return pos - ivl.start

def normalise(ivl, length=None):
    try:
        return slice(ivl.start if ivl.start >= 0 else length + ivl.start,
            ivl.stop if ivl.stop >= 0 else length + ivl.stop, ivl.step)
    except TypeError:
        err = 'You must specify a length for splices with negative indices'
        raise TypeError(err)

