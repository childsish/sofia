import imp
import os

from sofia_.action import Action, Extractor, Resource, Target
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


def load_action_hypergraph(template):
    available_actions = load_plugins(template, Action, {Resource, Target})
    entity_graph = load_entity_graph(template)
    res = ActionHyperGraph(entity_graph)
    for action, root in available_actions:
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


def load_entity_graph(template):
    program_dir = get_program_directory()
    return EntityGraph(os.path.join(program_dir, 'templates', template, 'entities.json'))


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_plugins(template, parent_class, excluded=set()):
    import sys

    plugins = []
    action_dir = os.path.join(get_program_directory(), 'templates', template, 'actions')
    sys.path.append(action_dir)
    for fname in os.listdir(action_dir):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(action_dir, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues()
                         if type(child_class) == type and child_class.__name__ != parent_class.__name__]
        for child_class in child_classes:
            if issubclass(child_class, parent_class) and child_class not in excluded:
                plugins.append((child_class, template))
    return plugins
