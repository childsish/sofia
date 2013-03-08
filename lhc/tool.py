import numpy as np

from collections import deque
from itertools import repeat

class enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

def window(iterable, n=2, cast=tuple):
    """ This function passes a running window along the length of the given
        iterable.  By default, the return value is a tuple, but the cast
        parameter can be used to change the final result.
    """
    it = iter(iterable)
    win = deque((next(it) for _ in repeat(None, n)), maxlen=n)
    if len(win) < n:
        raise ValueError('Window size was greater than iterable length')
    yield cast(win)
    append = win.append
    for e in it:
        append(e)
        yield cast(win)

def combinations_with_replacement(iterable, r):
    """ This function acts as a replacement for the
        itertools.combinations_with_replacement function. The original does not
        replace items that come earlier in the provided iterator.
    """
    stk = [[i,] for i in iterable]
    pop = stk.pop
    while len(stk) > 0:
        top = pop()
        if len(top) == r:
            yield tuple(top)
        else:
            stk.extend(top + [i] for i in iterable)

def gmean(seq):
    """ Calculate the geometric mean. """
    return np.exp(np.mean(np.log(np.array(seq))))
