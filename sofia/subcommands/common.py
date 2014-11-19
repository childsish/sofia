import os

from lhc.tools import loadPlugins
from ebias.features import Feature
from ebias.feature_wrapper import FeatureWrapper
from ebias.feature_hyper_graph import FeatureHyperGraph
from ebias.entity_graph import EntityGraph

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
    res = FeatureHyperGraph(loadEntityGraph())
    for feature in available_features.itervalues():
        res.registerFeature(FeatureWrapper(feature))
    return res

def loadEntityGraph():
    program_dir = getProgramDirectory()
    return EntityGraph(os.path.join(program_dir, 'entities.json'))

def getProgramDirectory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]

