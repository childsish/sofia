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

def getProgramDirectory():
    return os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 2)[0]
