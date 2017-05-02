import os
import re

from sofia.entity_type import EntityType


class EntityDefinitionParser(object):
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

    def __init__(self, extensions):
        self.extensions = extensions

    def parse_requested_entity(self, definition):
        try:
            type, alias, attributes = self.parse_definition(definition)
        except Exception:
            raise ValueError('Invalid entity definition: {}'.format(definition))

        match = self.REGX.match(type)
        if match is None:
            raise ValueError('Invalid entity type: {}'.format(type))
        type, format_string = match.groups('')
        return EntityType(type, attributes=attributes, alias=alias, format_string=format_string)

    def parse_provided_entity(self, definition):
        filename, alias, attributes = self.parse_definition(definition)
        type = self.get_type_by_extension(filename)
        attributes['filename'] = {filename}
        if alias is None:
            alias = os.path.basename(filename)
        attributes['resource'] = {alias}
        return EntityType(type, attributes=attributes, alias=alias)

    def parse_definition(self, definition):
        """
        Parse the basic structure of both provided and requested entities

        :param definition: string encoding an entity
        :return: tuple of entity type, alias and attributes
        """
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
                raise ValueError('entity name already defined: {}'.format(part))
        return type, alias, attributes

    def get_type_by_extension(self, filename):
        for extension in self.extensions:
            if filename.endswith(extension):
                return self.extensions[extension]
        return None
