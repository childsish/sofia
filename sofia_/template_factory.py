import imp
import os
import sys
from collections import OrderedDict

from step import Step, Resource, Target, Extractor
from step.txt import TxtSet, TxtIterator, TxtAccessor
from step.map import GetIdById, Map
from wrappers.step_wrapper import StepWrapper
from wrappers.resource_wrapper import ResourceWrapper
from graph.template import Template
from graph.entity_graph import EntityGraph
from entity import Entity
from lhc.io.txt_ import FormatParser
from subcommands.common import load_steps


class TemplateFactory(object):
    def __init__(self, root):
        self.root = root
        self.steps = load_steps(os.path.join(root, 'steps'))
        self.recognised_formats = {step.FORMAT for step in self.steps if issubclass(step, Resource)}

    def make(self, provided_resources, requested_entities=[]):
        template = self.load_template()
        for step in self.load_custom_steps(provided_resources):
            template.register_step(step)
        for entity in requested_entities:
            template.register_entity(entity.name)
        template = self.add_extractors(template)
        return template

    def load_template(self):
        entity_graph = self.load_entity_graph()
        template = Template(entity_graph)
        for step in self.steps:
            if issubclass(step, Resource):
                template.register_step(ResourceWrapper(step))
            else:
                template.register_step(StepWrapper(step))
        template.register_step(StepWrapper(GetIdById))
        template.register_step(StepWrapper(Map))
        return template

    def load_custom_steps(self, provided_resources):
        entity_registry = self.get_entity_registry()
        index_registry = self.get_index_registry()

        res = []
        for name, resource in provided_resources.iteritems():
            if resource.format is not None and resource.format not in self.recognised_formats:
                entry_factory = entity_registry.parse_definition(resource.format)
                if resource.name == 'target':
                    outs = OrderedDict((out, Entity(out)) for out in entry_factory.type._fields) if entry_factory.name == 'Entry' else\
                        OrderedDict([(entry_factory.name, Entity(entry_factory.name))])
                    outs['target'] = Entity('target')
                    param = {
                        'entry': entry_factory,
                        'skip': int(resource.attr.get('skip', 0))
                    }
                    step = ResourceWrapper(TxtIterator, outs=outs, param=param, format=resource.format)
                    res.append(step)
                else:
                    if 'index' not in resource.attr:
                        import sys
                        sys.stderr.write('{} missing "index" attribute. '
                                         'Custom resources must have these attributes'.format(resource.name))
                        sys.exit(1)
                    index, index_key = index_registry.parse_definition(resource.attr['index'])
                    param = {
                        'entry': entry_factory,
                        'index': index,
                        'key': (lambda x: x[index_key]),
                        'skip': int(resource.attr.get('skip', 0))
                    }
                    step = ResourceWrapper(TxtSet,
                                           outs=OrderedDict([(resource.format, Entity(resource.format))]),
                                           param=param,
                                           format=resource.format)
                    res.append(step)
                    for in_ in resource.ins:
                        ins = OrderedDict([(resource.format, Entity(resource.format)),
                                           (in_, Entity(resource.ins[0]))])
                        outs = OrderedDict([(out, Entity(out)) for i, out in enumerate(entry_factory.type._fields)
                                           if i != index_key])
                        step = StepWrapper(TxtAccessor, '{}[{}]'.format(resource.format, in_), ins=ins, outs=outs, param={
                            'set_name': resource.format,
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
                extractors[(in_, out)] = path

        redundant = set()
        for in_, out in extractors:
            for equivalent in entity_graph.get_equivalent_descendents(in_) - {in_}:
                key = (equivalent, out)
                if key in extractors:
                    redundant.add(key)
                    break
        for key in redundant:
            del extractors[key]

        for (in_, out), path in extractors.iteritems():
            extractor = StepWrapper(Extractor,
                                    'Get{}From{}'.format(entity_graph.get_entity_name(out),
                                                         entity_graph.get_entity_name(in_)),
                                    ins={in_: entity_graph.create_entity(in_)},
                                    outs={out: entity_graph.create_entity(out)},
                                    param={'path': path})
            template.register_step(extractor)
        return template

    def load_entity_graph(self):
        return EntityGraph(os.path.join(self.root, 'entities.json'))

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

    def load_steps(self):
        steps = []
        step_dir = os.path.join(self.root, 'steps')
        sys.path.append(step_dir)
        for fname in os.listdir(step_dir):
            if fname.startswith('.') or not fname.endswith('.py'):
                continue
            module = imp.load_source(fname[:-3], os.path.join(step_dir, fname))
            types = [type_ for type_ in module.__dict__.itervalues() if type(type_) == type]
            print [(type_.__name__, issubclass(type_, Step), type_ not in {Step, Resource, Target}) for type_ in types]
            steps.extend(type_ for type_ in types if issubclass(type_, Step) and type_ not in {Step, Resource, Target})
        return steps
