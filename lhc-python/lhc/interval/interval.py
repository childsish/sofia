from functools import total_ordering
from collections import namedtuple


@total_ordering
class Interval(object):

    __slots__ = ('start', 'stop', 'data')

    INTERVAL_PAIR = namedtuple('IntervalPair', ('left', 'right'))

    def __init__(self, start, stop, data=None):
        self.start, self.stop = sorted((start, stop))
        self.data = data

    def __str__(self):
        return '[{start!r}, {stop!r})'.format(start=self.start, stop=self.stop)
    
    def __len__(self):
        return self.stop - self.start
    
    def __repr__(self):
        return 'Interval{s}'.format(s=str(self))
    
    def __eq__(self, other):
        return self.start == other.start and\
            self.stop == other.stop
    
    def __lt__(self, other):
        return self.stop < other.stop if self.start == other.start else self.start < other.start
    
    def __hash__(self):
        return hash((self.start, self.stop))

    def __contains__(self, item):
        """ Used for testing points

        :param item: point for testing
        :return: if the point is within the interval bounds
        """
        return self.start == item if self.start == self.stop else self.start <= item < self.stop
        
    # Relative location functions
    
    def overlaps(self, other):
        """Test if self and other overlap
        
        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.start < other.stop and other.start < self.stop
    
    def contains(self, other):
        """Test if self wholly contains 
    
        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.start <= other.start and other.stop <= self.stop
    
    def touches(self, other):
        """Test if self touches (but doesn't overlap) other
        
        :param Interval other: the interval being tested
        :rtype: bool
        """
        return self.start == other.stop or self.stop == other.start
    
    # Set-like operation functions
    
    def union(self, other):
        """Return the interval covering self and other if they overlap
        
        :param Interval other: the other interval
        :rtype: Interval or None
        """
        return Interval(min(self.start, other.start),
                        max(self.stop, other.stop))\
            if self.overlaps(other) or self.touches(other) else None

    def union_update(self, other):
        if not self.overlaps(other):
            raise ValueError('can not union non-overlapping intervals')
        self.start = min(self.start, other.start)
        self.stop = max(self.stop, other.stop)
    
    def intersect(self, other):
        """Return an interval where self and other intersect
        
        :param Interval other: the other interval
        :rtype: Interval or None 
        """
        return Interval(max(self.start, other.start),
                        min(self.stop, other.stop))\
            if self.overlaps(other) else None

    def intersect_update(self, other):
        if not self.overlaps(other):
            raise ValueError('can not intersect non-overlapping intervals')
        self.start = max(self.start, other.start)
        self.stop = min(self.stop, other.stop)
    
    def difference(self, other):
        """Return an interval that covers self but not other
        
        :param Interval other: interval to remove
        :rtype: 2-tuple of interval or None
        
        If there is no overlap, the result is at .left and .right is None
        If self is cut on the lower side, the result is at .right.
        If self is cut on the upper side, the result is at .left.
        If self is cut in the middle, the result in in both .left and .right
        """
        if not self.overlaps(other):
            return Interval.INTERVAL_PAIR(self, None)
        
        left, right = None
        if self.start < other.start:
            left = Interval(self.start, other.start)
        if other.stop < self.stop:
            right = Interval(other.stop, self.stop)
        return Interval.INTERVAL_PAIR(left, right)
    
    # Interval arithmetic functions
    
    def add(self, other):
        """Return the arithmetic addition of self and other
        
        :param Interval other: the other interval
        """
        return Interval(self.start + other.start, self.stop + other.stop)
    
    def subtract(self, other):
        """Return the arithmetic subtraction of self and other
        
        :param Interval other: the other interval
        """
        return Interval(self.start - other.stop, self.stop - other.start)
    
    def multiply(self, other):
        """Return the arithmetic multiplication of self and other
        
        :param Interval other: the other interval
        """
        return Interval(min(self.start * other.start, self.start * other.stop,
                            self.stop * other.start, self.stop * other.stop),
                        max(self.start * other.start, self.start * other.stop,
                            self.stop * other.start, self.stop * other.stop))
    
    def divide(self, other):
        """Return the arithmetic division of self and other
        
        :param Interval other: the other interval
        """
        return Interval(min(self.start / other.start, self.start / other.stop,
                            self.stop / other.start, self.stop / other.stop), 
                        max(self.start / other.start, self.start / other.stop,
                            self.stop / other.start, self.stop / other.stop))\
            if other.start != 0 and other.stop != 0 else None
    
    # Position functions
    
    def get_abs_pos(self, pos):
        """Get the absolute position of a position relative to a interval
        
        :param int pos: the position relative to the interval
    
        """
        if pos < 0 or pos >= self.stop - self.start:
            err = 'Relative position %d is not contained within %s'
            raise IndexError(err)
        return self.start + pos
    
    def get_rel_pos(self, pos):
        """Get the position relative to a interval of a position.
    
        :param int pos: the position to calculate relative to the interval
    
        """
        if pos < self.start or pos >= self.stop:
            err = 'Absolute position {} is not contained within {}'
            raise IndexError(err.format(pos, self))
        return pos - self.start
    
    # Sequence functions
    
    def get_sub_seq(self, seq):
        return seq[self.start:self.stop]
