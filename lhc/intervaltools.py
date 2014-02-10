"""Tools that manipulate intervals

Instead of creating a whole new Interval class, intervaltools allows any object
with .start and .stop members to be manipulated as intervals in one dimension.
This means slices can also be treated like intervals which is the best
compromise I could find for creating intervals that can also be used to slice
strings and lists.
WARNING: Slices with negative indices (ie. counting from the end of a sequence),
are incompatible with these functions.
"""

def overlaps(a, b):
    """Test if two intervals overlap
    
    Keyword arguments:
    :param interval a: interval A
    :param interval b: interval B
    """
    return a.start < b.stop and b.start < a.stop

def contains(a, b):
    """Test if interval a wholly contains interval b

    Keyword arguments:
    :param interval a: the interval that may contain
    :param interval b: the interval that may be contained
    """
    return a.start <= b.start and b.stop <= a.stop

def getAbsPos(ivl, pos):
    """Get the absolute position of a position relative to a interval
    
    Keyword arguments:
    :param interval ivl: interval to which the position is relative
    :param interval pos: the position relative to the interval

    """
    if pos < 0 or pos >= ivl.stop - ivl.start:
        err = 'Relative position %d is not contained within %s'
        raise IndexError(err)
    return ivl.start + pos

def getRelPos(ivl, pos):
    """Get the position relative to a interval of a position.

    Keyword arguments:
    :param interval ivl: the interval relative to which the position should be calculated
    :param int pos: the position to calculate relative to the interval

    """
    if pos < ivl.start or pos >= ivl.stop:
        err = 'Absolute position %d is not contained within %s'
        raise IndexError(err%(pos, ivl))
    return pos - ivl.start
