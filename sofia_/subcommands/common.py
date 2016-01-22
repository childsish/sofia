import imp
import json
import os

from sofia_.entity import Entity
from sofia_.parser.provided_entity_parser import ResourceParser
from sofia_.parser.requested_entity_parser import ProvidedEntityParser

from sofia_.step import Step, Resource, Target


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def parse_provided_resources(args, template_directory):
    fhndl = open(os.path.join(template_directory, 'provided_resources.txt'))
    provided_resource_definitions = [os.path.join(template_directory, 'data', line.strip())
                                     for line in fhndl if line.strip() != '']
    fhndl.close()

    provided_resource_definitions.append('{}:target'.format(args.input))
    if 'resource_list' in args and args.resource_list is not None:
        provided_resource_definitions.extend(line.rstrip('\r\n') for line in open(args.resource_list))
    if 'resources' in args:
        provided_resource_definitions.extend(args.resources)

    fhndl = open(os.path.join(template_directory, 'resource_entities.json'))
    resources = json.load(fhndl)
    fhndl.close()
    extensions = {}
    for resource in resources:
        for extension in resource['extensions']:
            if extension in extensions:
                raise KeyError('Extension "{}" defined multiple times.'.format(extension))
            extensions[extension] = resource['name']

    parser = ResourceParser(extensions)
    return parser.parse_resources(provided_resource_definitions)


def parse_requested_entities(args, provided_resources):
    requested_entity_definitions = []
    if 'entity_list' in args and args.entity_list is not None:
        requested_entity_definitions.extend(line.rstrip('\r\n') for line in open(args.entity_list))
    if 'entities' in args:
        requested_entity_definitions.extend(args.entities)
    parser = ProvidedEntityParser(provided_resources)
    return parser.parse_entity_requests(requested_entity_definitions)


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_steps(plugin_dir):
    import os
    import sys

    format_error = 'Unable to import step {}. Parameter "format" is reserved and can not be used in attribute PARAMS.'

    plugins = []
    sys.path.append(plugin_dir)
    for fname in os.listdir(plugin_dir):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(plugin_dir, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues()
                         if type(child_class) == type]
        for child_class in child_classes:
            if issubclass(child_class, Step) and child_class not in {Step, Resource, Target}:
                if 'format' in child_class.PARAMS:
                    raise ImportError(format_error.format(child_class.__name__))
                plugins.append(child_class)
    return plugins
