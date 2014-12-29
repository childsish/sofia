import os
import imp

from sofia_.action import Action, Extractor
from sofia_.action_wrapper import ActionWrapper
from sofia_.graph.action_hyper_graph import ActionHyperGraph
from sofia_.graph.entity_graph import EntityGraph


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def load_action_hypergraph():
    program_dir = get_program_directory()
    available_actions = load_plugins(os.path.join(program_dir, 'actions'), Action)
    entity_graph = load_entity_graph()
    res = ActionHyperGraph()
    for action in available_actions.itervalues():
        res.register_action(ActionWrapper(action))
    for in_ in set(res.entities):
        if in_ not in entity_graph.graph.vs:
            continue
        for out in entity_graph.graph.get_children(in_):
            extractor_name = 'Get{}From{}'.format(entity_graph.get_entity_name(out), entity_graph.get_entity_name(in_))
            extractor = ActionWrapper(Extractor,
                                      extractor_name,
                                      ins={in_: entity_graph.create_entity(in_)},
                                      outs={out: entity_graph.create_entity(out)},
                                      param={'path': [in_, out]})
            res.register_action(extractor)
    return res


def load_entity_graph():
    program_dir = get_program_directory()
    return EntityGraph(os.path.join(program_dir, 'entities.json'))


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_plugins(indir, cls):
    import os
    import sys

    sys.path.append(indir)
    sys.path.append(os.path.join(indir, 'modules'))
    plugins = {}

    fnames = (fname for fname in os.listdir(indir) if fname[0] != '.' and fname.endswith('.py'))
    for fname in fnames:
        module_name, ext = os.path.splitext(fname)
        d = imp.load_source(module_name, os.path.join(indir, fname)).__dict__
        for k, v in d.iteritems():
            if k == cls.__name__:
                continue
            try:
                if issubclass(v, cls):
                    plugins[k] = v
            except TypeError:
                continue
    return plugins
