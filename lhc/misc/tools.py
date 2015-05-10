import imp

from collections import deque
from itertools import repeat


class enum(set):
    def __contains__(self, key):
        return super(enum, self).__contains__(key)
    
    def __getitem__(self, key):
        if key in self:
            return key
        raise KeyError 
    
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


def argsort(seq, cmp=None, key=None):
    key = seq.__getitem__ if key is None else lambda x:key(seq[x])
    return sorted(range(len(seq)), cmp=cmp, key=key)


def load_plugins(plugin_dir, parent_class, excluded=set()):
    import os
    import sys

    plugins = []
    sys.path.append(plugin_dir)
    for fname in os.listdir(plugin_dir):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(plugin_dir, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues()
                         if type(child_class) == type and child_class.__name__ != parent_class.__name__]
        for child_class in child_classes:
            if issubclass(child_class, parent_class) and child_class not in excluded:
                plugins.append(child_class)
    return plugins


def accumulate(xs):
    ttl = 0
    for x in xs:
        ttl += x
        yield ttl
