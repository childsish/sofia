"""Tools that manipulate intervals

Instead of creating a whole new Interval class, intervaltools allows any object
with .start and .stop members to be manipulated as intervals in one dimension.
This means slices can also be treated like intervals which is the best
compromise I could find for creating intervals that can also be used to slice
strings and lists.
WARNING: Slices with negative indices (ie. counting from the end of a sequence),
are incompatible with these functions.
"""
from collections import namedtuple

def overlaps(a, b):
    """Test if two intervals overlap
    
    :param interval a: interval A
    :param interval b: interval B
    :rtype: bool
    """
    return a.start < b.stop and b.start < a.stop

def contains(a, b):
    """Test if interval a wholly contains interval b

    :param interval a: the interval that may contain
    :param interval b: the interval that may be contained
    :rtype: bool
    """
    return a.start <= b.start and b.stop <= a.stop

def union(a, b):
    """Return an interval that is the union of the two
    
    This actually returns a slice, which should work with all intersection
    functions that use the .start and .stop attributes.
    
    :param interval a: interval A
    :param interval b: interval B
    :rtype: 2-tuple of interval or None.
    """
    if overlaps(a, b):
        return IntervalPair(slice(min(a.start, b.start), max(a.stop, b.stop)), None)
    return IntervalPair(a, b)

def intersect(a, b):
    """Return an interval where a and b intersect
    
    This actually returns a slice, which should work with all intersection
    functions that use the .start and .stop attributes.
    
    :param interval a: interval A
    :param interval b: interval B
    :rtype: slice or None 
    """
    if overlaps(a, b):
        return slice(max(a.start, b.start), min(a.stop, b.stop))
    return None

def difference(a, b):
    """Return an interval that covers a but not b
    
    This actually returns a slice, which should work with all intersection
    functions that use the .start and .stop attributes.
    
    :param interval a: interval A
    :param interval b: interval B
    :rtype: 2-tuple of interval or None 
    """
    if not overlaps(a, b):
        return IntervalPair(a, None)
    
    left, right = None
    if a.start < b.start:
        left = slice(a.start, b.start)
    if b.stop < a.stop:
        right = interval(b.stop, a.stop)
    return IntervalPair(left, right)

def getAbsPos(ivl, pos):
    """Get the absolute position of a position relative to a interval
    
    :param interval ivl: interval to which the position is relative
    :param interval pos: the position relative to the interval

    """
    if pos < 0 or pos >= ivl.stop - ivl.start:
        err = 'Relative position %d is not contained within %s'
        raise IndexError(err)
    return ivl.start + pos

def getRelPos(ivl, pos):
    """Get the position relative to a interval of a position.

    :param interval ivl: the interval relative to which the position should be calculated
    :param int pos: the position to calculate relative to the interval

    """
    if pos < ivl.start or pos >= ivl.stop:
        err = 'Absolute position %d is not contained within %s'
        raise IndexError(err%(pos, ivl))
    return pos - ivl.start

IntervalPair = namedtuple('IntervalPair', ('left', 'right'))