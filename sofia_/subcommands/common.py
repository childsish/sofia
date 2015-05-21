import imp
import os

from sofia_.parser.resource_parser import ResourceParser
from sofia_.parser.entity_parser import EntityParser

from sofia_.step import Step, Resource, Target


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def parse_provided_resources(args):
    provided_resource_definitions = []
    if args.input is not None:
        provided_resource_definitions.append(args.input + ' -n target')
    if args.resource_list is not None:
        provided_resource_definitions.extend(line.rstrip('\r\n') for line in open(args.resource_list))
    provided_resource_definitions.extend(args.resources)
    parser = ResourceParser()
    return parser.parse_resources(provided_resource_definitions)


def parse_requested_entities(args, provided_resources):
    requested_entity_definitions = []
    if args.entity_list is not None:
        requested_entity_definitions.extend(line.rstrip('\r\n') for line in open(args.entity_list))
    requested_entity_definitions.extend(args.entities)
    if len(requested_entity_definitions) == 0:
        import sys
        sys.stderr.write('Error: No entities were requested. Please provide'
                         'the names of the entities you wish to calculate.')
        sys.exit(1)
    parser = EntityParser(provided_resources)
    return parser.parse_entity_requests(requested_entity_definitions)


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_steps(plugin_dir):
    import os
    import sys

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
                plugins.append(child_class)
    return plugins
