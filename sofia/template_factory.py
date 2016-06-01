import imp
import inspect
import json
import os
import sys

from graph.entity_graph import EntityGraph
from graph.template import Template
from resolvers import AttributeResolver
from sofia.step import StepWrapper
from step import Step, Extractor


class TemplateFactory(object):
    def __init__(self, root):
        self.root = root
        self.entity_graph = self.load_entity_graph(os.path.join(self.root, 'entities.json'))
        self.steps = self.load_steps(os.path.join(root, 'steps'))
        self.attributes = self.load_attributes(os.path.join(root, 'attributes'))
        with open(os.path.join(root, 'resource_entities.json')) as fhndl:
            self.recognised_formats = {definition['name'] for definition in json.load(fhndl)}

    def make(self, provided_entities=None, requested_entities=None):
        provided_entities = [] if provided_entities is None else provided_entities
        requested_entities = [] if requested_entities is None else requested_entities

        template = self.load_template()
        for entity in provided_entities:
            template.register_entity(entity.name)
        for entity in requested_entities:
            template.register_entity(entity.name)
        template = self.add_extractors(template)
        return template

    def load_template(self):
        template = Template(self.entity_graph)
        for step in self.steps:
            template.register_step(StepWrapper(step))
        for attribute in self.attributes:
            template.register_attribute(attribute)
        return template

    def add_extractors(self, template):
        entity_graph = template.entity_graph
        entities = set(template.entities)
        extractors = {}
        for in_ in entities:
            if in_ not in entity_graph:
                continue
            for path in entity_graph.get_descendent_paths(in_):
                out = path[-1]['name']
                if out not in entities:
                    continue
                extractors[(in_, out)] = (path, 'Get{}From{}'.format(entity_graph.get_entity_name(out),
                                                                     entity_graph.get_entity_name(in_)))
            for out in entity_graph.get_equivalent_ancestors(in_) - {in_}:
                extractors[(in_, out)] = ([], 'Cast{}To{}'.format(entity_graph.get_entity_name(in_),
                                                                  entity_graph.get_entity_name(out)))

        for (in_, out), (path, name) in extractors.iteritems():
            extractor = StepWrapper(Extractor,
                                    name,
                                    ins={in_: entity_graph.create_entity(in_)},
                                    outs={out: entity_graph.create_entity(out)},
                                    attr={'path': path})
            template.register_step(extractor)
        return template

    def load_entity_graph(self, filename):
        return EntityGraph(filename)

    def load_steps(self, step_directory):
        steps = self.load_plugins(step_directory, Step)
        for step in steps:
            if 'format' in step.PARAMS:
                msg = 'Unable to import step {}. Parameter "format" is reserved and can not be used in attribute PARAMS.'
                raise ImportError(msg.format(step.__name__))
        return steps

    def load_attributes(self, attribute_directory):
        return self.load_plugins(attribute_directory, AttributeResolver)

    def load_plugins(self, plugin_directory, plugin_class, exclude=None):
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


def inherits_from(child, parent_name):
    if inspect.isclass(child):
        if parent_name in {c.__name__ for c in inspect.getmro(child)[1:]}:
            return True
    return False
