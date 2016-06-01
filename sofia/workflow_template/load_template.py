import imp
import json
import os
import sys

from entity_graph import EntityGraph
from template import Template
from sofia.resolvers import AttributeResolver
from sofia.step import Step, Extractor, ConcreteStep


def load_template(root):
    entities = load_entities(os.path.join(root, 'entities.json'))
    steps = load_steps(os.path.join(root, 'steps'))
    steps.update(get_extractors(entities))
    attributes = load_attributes(os.path.join(root, 'attributes'))

    template = Template(entities, steps, attributes)
    return template


def load_entities(filename):
    with open(filename) as fileobj:
        entities = json.load(fileobj)

    entities = {entity['name']: entity for entity in entities}
    for entity in entities.itervalues():
        entity['has_a'] = {child['name']: child for child in entity.get('has_a', [])}
    graph = EntityGraph(entities)

    for entity in entities.itervalues():
        graph.has_a.add_vertex(entity['name'])
        for child in entity.get('has_a', []):
            graph.has_a.add_edge(entity['name'], child)
        if 'is_a' in entity:
            graph.is_a.add_edge(entity['is_a'], entity['name'])
        if 'attributes' in entity:
            graph.attr[entity['name']] = entity['attributes']
    return graph


def load_steps(step_directory):
    steps = load_plugins(step_directory, Step)
    for step in steps:
        if 'format' in step.PARAMS:
            msg = 'Unable to import step {}. Parameter "format" is reserved and can not be used in attribute PARAMS.'
            raise ImportError(msg.format(step.__name__))
    return {step.__name__: ConcreteStep(step) for step in steps}


def load_attributes(attribute_directory):
    attributes = load_plugins(attribute_directory, AttributeResolver)
    return {attribute.ATTRIBUTE: attribute for attribute in attributes}


def load_plugins(plugin_directory, plugin_class, exclude=None):
    if exclude is None:
        exclude = {plugin_class}
    else:
        exclude |= {plugin_class}

    plugins = []
    sys.path.append(plugin_directory)
    for fname in os.listdir(plugin_directory):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(plugin_directory, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues() if type(child_class) == type]
        for child_class in child_classes:
            if issubclass(child_class, plugin_class) and child_class not in exclude:
                plugins.append(child_class)
    return plugins


def get_extractors(entities):
    extractors = {}
    for in_ in entities:
        for path in entities.get_descendent_paths(in_):
            out = path[-1]['name']
            extractors[(in_, out)] = (path, 'Get{}From{}'.format(entities.get_entity_name(out),
                                                                 entities.get_entity_name(in_)))
        for out in entities.get_equivalent_ancestors(in_) - {in_}:
            extractors[(in_, out)] = ([], 'Cast{}To{}'.format(entities.get_entity_name(in_),
                                                              entities.get_entity_name(out)))
    res = {}
    for (in_, out), (path, name) in extractors.iteritems():
        res[name] = ConcreteStep(Extractor, name, [in_], [out], {'path': path})
    return res
