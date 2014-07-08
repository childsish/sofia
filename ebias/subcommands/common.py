import os
import sys

from lhc.tools import loadPlugins
from ebias.feature import Feature
from ebias.feature_hyper_graph import FeatureHyperGraph

def loadResource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: %s'%\
        os.path.basename(fname))

def loadFeatureHyperGraph():
    program_dir = getProgramDirectory()
    available_features = loadPlugins(os.path.join(program_dir, 'features'), Feature)
    res = FeatureHyperGraph()
    for feature in available_features.itervalues():
        res.registerFeature(feature)
    return res

def getProgramDirectory():
    return os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 2)[0]
