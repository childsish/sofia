from collections import deque
from itertools import repeat

def window(seq, n=2):
    it = iter(seq)
    win = deque((next(it, None) for _ in repeat(None, n)), maxlen=n)
    yield win
    append = win.append
    for e in it:
        append(e)
        yield win

def combinations_with_replacement(iterable, r):
    stk = [[i,] for i in iterable]
    pop = stk.pop
    while len(stk) > 0:
        top = pop()
        if len(top) == r:
            yield tuple(top)
        else:
            stk.extend(top + [i] for i in iterable)
