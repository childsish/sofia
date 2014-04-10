import os
import sys

def loadResource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: %s'%\
        os.path.basename(fname))

def loadPlugins(indir, cls):
    sys.path.insert(0, indir)
    plugins = {}

    mnames = (fname[:-3] for fname in os.listdir(indir)\
        if fname[0] != '.' and fname.endswith('.py'))

    for mname in mnames:
        d = __import__(mname).__dict__
        for k, v in d.iteritems():
            if k == cls.__name__:
                continue
            try:
                if issubclass(v, cls):
                    plugins[v.NAME] = v
            except TypeError:
                continue
    return plugins
