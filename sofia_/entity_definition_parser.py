from collections import namedtuple


EntityDefinition = namedtuple('EntityDefinition', ('type', 'alias', 'attributes'))


def parse_entity_definition(definition):
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

    :param definition: string defining an entity
    :return: EntityDefinition with the variable part, name and attributes
    """
    parts = definition.split(':')
    type = parts[0]
    alias = None
    attributes = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            attributes[key] = value
        elif alias is None:
            alias = part
        else:
            raise ValueError('entity name already defined')
    return EntityDefinition(type, alias, attributes)
