import os

from lhc.tools import loadPlugins

from sofia_.action import Action
from sofia_.action_wrapper import ActionWrapper
from sofia_.graph.action_hyper_graph import ActionHyperGraph
from sofia_.graph.entity_graph import EntityGraph

def loadResource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: %s'%\
        os.path.basename(fname))

def loadActionHyperGraph():
    program_dir = getProgramDirectory()
    available_actions = loadPlugins(os.path.join(program_dir, 'actions'), Action)
    res = ActionHyperGraph(loadEntityGraph())
    for action in available_actions.itervalues():
        res.registerAction(ActionWrapper(action))
    return res

def loadEntityGraph():
    program_dir = getProgramDirectory()
    return EntityGraph(os.path.join(program_dir, 'entities.json'))

def getProgramDirectory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]
