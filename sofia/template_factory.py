import imp
import inspect
import json
import os
import sys
from collections import OrderedDict

from entity_type import EntityType
from graph.entity_graph import EntityGraph
from graph.template import Template
from lhc.io.txt import FormatParser
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
        for step in self.load_custom_steps(provided_entities):
            template.register_step(step)
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

    def load_custom_steps(self, provided_entities):
        entity_registry = self.get_entity_registry()
        index_registry = self.get_index_registry()

        res = []
        for entity in provided_entities:
            if entity.name is not None and entity.name not in self.recognised_formats:
                try:
                    entry_factory = entity_registry.parse(entity.name)
                except KeyError, e:
                    if e.message in {'/', '\\'}:
                        raise IOError('[Errno 2] No such file or directory: {}'.format(entity.name))
                    else:
                        raise e
                if entity.name == 'target':
                    outs = OrderedDict((out, EntityType(out)) for out in entry_factory.type._fields) if entry_factory.name == 'Entry' else\
                        OrderedDict([(entry_factory.name, EntityType(entry_factory.name))])
                    outs['target'] = EntityType('target')
                    param = {
                        'entry': entry_factory,
                        'skip': int(entity.attr.get('skip', 0))
                    }
                    step = StepWrapper(TxtIterator, outs=outs, param=param, format=entity.name)
                    res.append(step)
                else:
                    if 'index' not in entity.attr:
                        import sys
                        sys.stderr.write('{} missing "index" attribute. '
                                         'Custom resources must have these attributes'.format(entity.name))
                        sys.exit(1)
                    index, index_key = index_registry.parse_definition(entity.attr['index'])
                    param = {
                        'entry': entry_factory,
                        'index': index,
                        'key': (lambda x: x[index_key]),
                        'skip': int(entity.attr.get('skip', 0))
                    }
                    step = StepWrapper(TxtSet,
                                           outs=OrderedDict([(entity.name, EntityType(entity.name))]),
                                           param=param,
                                           format=entity.name)
                    res.append(step)
                    for in_ in entity.ins:
                        ins = OrderedDict([(entity.name, EntityType(entity.name)),
                                           (in_, EntityType(entity.ins[0]))])
                        outs = OrderedDict([(out, EntityType(out)) for i, out in enumerate(entry_factory.type._fields)
                                            if i != index_key])
                        step = StepWrapper(TxtAccessor, '{}[{}]'.format(entity.name, in_), ins=ins, outs=outs, attr={
                            'set_name': entity.name,
                            'key_name': in_
                        })
                        res.append(step)
        return res

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

    def get_index_registry(self):
        return
        #registry = IndexParser()
        #path = os.path.join(self.root, 'index_registry.py')
        #for k, v in imp.load_source('index_registry', path).INDEX_REGISTRY.iteritems():
        #    registry.register_index(k, v)
        #return registry

    def get_entity_registry(self):
        registry = FormatParser()
        path = os.path.join(self.root, 'entity_registry.py')
        for k, v in imp.load_source('entity_registry', path).ENTITY_REGISTRY.iteritems():
            registry.register_type(k, v)
        return registry

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
