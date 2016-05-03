from __future__ import with_statement

import imp
import json
import os
import re

from sofia_.entity import Entity
from sofia_.entity_definition_parser import parse_entity_definition
from sofia_.step import Step, Resource, Target


def load_resource(fname, parsers, format=None):
    if format is not None and format in parsers:
        return parsers[format](fname)
    for format in parsers:
        if fname.endswith(format):
            return parsers[format](fname)
    raise TypeError('Unrecognised file format: {}'.format(os.path.basename(fname)))


def get_extension_entity_map(template_directory):
    with open(os.path.join(template_directory, 'resource_entities.json')) as fhndl:
        resources = json.load(fhndl)
    extensions = {}
    for resource in resources:
        for extension in resource['extensions']:
            if extension in extensions:
                raise KeyError('Extension "{}" defined multiple times.'.format(extension))
            extensions[extension] = resource['name']
    return extensions


def get_provided_entities(template_directory, definitions=[], definition_file=None):
    definitions_ = []
    with open(os.path.join(template_directory, 'provided_entities.txt')) as fhndl:
        definitions_.extend(os.path.join(template_directory, 'data', line.rstrip('\r\n')).split()
                           for line in fhndl if line.strip() != '')
    if definition_file is not None:
        with open(definition_file) as fhndl:
            definitions_.extend(line.rstrip('\r\n') for line in fhndl)
    if len(definitions) > 0:
        definitions_.extend(definitions)

    extensions = get_extension_entity_map(template_directory)
    return [get_provided_entity(definition, extensions) for definition in definitions_]


def get_provided_entity(definition, extensions):
    type, alias, attributes = parse_entity_definition(definition)

    if alias is None:
        alias = os.path.basename(type)
    if os.path.exists(type) or '/' in type or '\\' in type:
        attributes['filename'] = type

    if 'entity' in attributes:
        type = attributes['entity']
        del attributes['entity']
    elif 'filename' in attributes:
        type = get_type_by_extension(attributes['filename'], extensions)
        if type is None:
            raise ValueError('Provided entity {} has unknown extension or entity type is not explicitly defined'.format(alias))

    return Entity(type, {alias}, alias=alias, attr=attributes)


def get_type_by_extension(filename, extensions):
    for extension in extensions:
        if filename.endswith(extension):
            return extensions[extension]
    return None


def get_requested_entities(args, provided_entities):
    definitions = []
    if args.entity_list is not None:
        definitions.extend(line.rstrip('\r\n') for line in open(args.entity_list))
    if args.entities is not None:
        definitions.extend(args.entities)

    return [get_requested_entity(definition) for definition in definitions]


def get_requested_entity(definition):
    REGX = re.compile(r'(?P<entity>[^[.:]+)(?P<getter>[^:]+)?')

    type, alias, attributes = parse_entity_definition(definition)
    match = REGX.match(type)
    if match is None:
        raise ValueError('Invalid entity definition: {}'.format(type))
    type = match.group('entity')
    getter = '' if match.group('getter') is None else match.group('getter')
    return Entity(type, alias=alias, attr=attributes, getter=getter)


def get_program_directory():
    return os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 2)[0]


def load_steps(step_directory):
    import os
    import sys

    format_error = 'Unable to import step {}. Parameter "format" is reserved and can not be used in attribute PARAMS.'

    steps = []
    sys.path.append(step_directory)
    for fname in os.listdir(step_directory):
        if fname.startswith('.') or not fname.endswith('.py'):
            continue
        module_name, ext = os.path.splitext(fname)
        module = imp.load_source(module_name, os.path.join(step_directory, fname))
        child_classes = [child_class for child_class in module.__dict__.itervalues()
                         if type(child_class) == type]
        for child_class in child_classes:
            if issubclass(child_class, Step) and child_class not in {Step, Resource, Target}:
                if 'format' in child_class.PARAMS:
                    raise ImportError(format_error.format(child_class.__name__))
                steps.append(child_class)
    return steps
