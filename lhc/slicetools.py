"""Tools that treat slices like intervals."""

def overlaps(a, b, length=None):
    """Test if two slices overlap
    
    Keyword arguments:
    a -- slice A
    b -- slice B
    length -- only slices with positive indices can be compared. If any of the indices are negative, provide the length to normalise those slices.
    
    """
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start < b.stop and b.start < a.stop

def contains(a, b, length=None):
    """Test if slice a wholly contains slice b

    Keyword arguments:
    a -- the slice that may contain
    b -- the slice that may be contained
    length -- only slices with positive indices can be compared. If any of the indices are negative, provide the length to normalise those slices.

    """
    a = normalise(a, length)
    b = normalise(b, length)
    return a.start <= b.start and a.stop >= b.stop

def getAbsPos(slc, pos, length=None):
    """Get the absolute position of a position relative to a slice
    
    Keyword arguments:
    slc -- slice to which the position is relative
    pos -- the position relative to the slice

    """
    slc = normalise(slc, length)
    if pos < 0 or pos >= slc.stop - slc.start:
        err = 'Relative position %d is not contained within %s'
        raise IndexError(err)
    return slc.start + pos

def getRelPos(slc, pos, length=None):
    """Get the position relative to a slice of a position.

    Keyword arguments:
    slc -- the slice relative to which the position should be calculated
    pos -- the position to calculate relative to the slice

    """
    slc = normalise(slc, length)
    if pos < slc.start or pos >= slc.stop:
        err = 'Absolute position %d is not contained within %s'
        raise IndexError(err%(pos, slc))
    return pos - slc.start

def normalise(slc, length=None):
    try:
        return slice(slc.start if slc.start >= 0 else length + slc.start,
            slc.stop if slc.stop >= 0 else length + slc.stop, slc.step)
    except TypeError:
        err = 'You must specify a length for splices with negative indices'
        raise TypeError(err)

