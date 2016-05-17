from __future__ import with_statement

import json
import os
import re

from collections import namedtuple
from entity_type import EntityType


EntityDefinition = namedtuple('EntityDefinition', ('type', 'alias', 'attributes'))


class EntityTypeParser(object):
    """ A parser for resources on the command line and from resource files.

    The resource string takes the form of:
        <provided_resource> ::= <type_or_filename>[:<name>][:<attribute>[:<attribute>]*]
        <attribute> ::= <key>=<value>[,<value>]*
    where
        type_or_filename
            is the entity type or the file name of a resource
        <name>
            is the name of the entity
        <key>
            is the name of an attribute
        <value>
            is the value of an attribute

    An example:
        -r /tmp/tmp.vcf
        -r "/tmp/tmp.vcf:tmp:entity=vcf"
        -r "tmp.vcf:tmp:format=vcf:x=x:y=y:chromosome_id=ucsc"
    """

    REGX = re.compile(r'(?P<entity>[^[.:]+)(?P<format_string>[^:]+)?')

    def __init__(self, template_directory):
        self.template_directory = template_directory
        self.extensions = self.get_extension_entity_map()

    def get_requested_entities(self, args, provided_entities):
        definitions = []
        if args.entity_list is not None:
            definitions.extend(line.rstrip('\r\n') for line in open(args.entity_list))
        if args.entities is not None:
            definitions.extend(args.entities)

        return [self.get_requested_entity(definition) for definition in definitions]

    def get_requested_entity(self, definition):
        type, alias, attributes = self.parse_entity_type(definition)
        match = self.REGX.match(type)
        if match is None:
            raise ValueError('Invalid entity definition: {}'.format(type))
        type = match.group('entity')
        format_string = '' if match.group('format_string') is None else match.group('format_string')
        return EntityType(type, alias=alias, attributes=attributes, format_string=format_string)

    def get_provided_entities(self, definitions=None, definition_file=None):
        if definitions is None:
            definitions = []

        definitions_ = []
        with open(os.path.join(self.template_directory, 'provided_entities.txt')) as fhndl:
            definitions_.extend(os.path.join(self.template_directory, 'data', line.rstrip('\r\n')).split()
                                for line in fhndl if line.strip() != '')
        if definition_file is not None:
            with open(definition_file) as fhndl:
                definitions_.extend(line.rstrip('\r\n') for line in fhndl)

        return [self.get_provided_entity(definition) for definition in definitions_]

    def get_provided_entity(self, definition):
        type, alias, attributes = self.parse_entity_type(definition)

        if alias is None:
            alias = os.path.basename(type)
        if os.path.exists(type):
            attributes['filename'] = {type}

        if 'entity' in attributes:
            type = list(attributes['entity'])[0]
            del attributes['entity']
        elif 'filename' in attributes:
            type = self.get_type_by_extension(list(attributes['filename'])[0])
            if type is None:
                msg = 'Provided entity {} has unknown extension or entity type is not explicitly defined'
                raise ValueError(msg.format(alias))

        attributes['resource'] = {alias}
        return EntityType(type, alias=alias, attributes=attributes)

    def get_extension_entity_map(self):
        with open(os.path.join(self.template_directory, 'resource_entities.json')) as fhndl:
            resources = json.load(fhndl)
        extensions = {}
        for resource in resources:
            for extension in resource['extensions']:
                if extension in extensions:
                    raise KeyError('Extension "{}" defined multiple times.'.format(extension))
                extensions[extension] = resource['name']
        return extensions

    def get_type_by_extension(self, filename):
        for extension in self.extensions:
            if filename.endswith(extension):
                return self.extensions[extension]
        return None

    def parse_entity_type(self, definition):
        type = definition[0]
        alias = None
        attributes = {}
        for part in definition[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                attributes[key] = set(value.split(','))
            elif alias is None:
                alias = part
            else:
                raise ValueError('entity name already used: {}'.format(part))
        return EntityDefinition(type, alias, attributes)
