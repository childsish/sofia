import json

from sofia.workflow_template.entity_set import EntitySet
from sofia.workflow_template.entity_definition_parser import EntityDefinitionParser


def load_entity_set(filename):
    with open(filename) as fileobj:
        entity_definitions = json.load(fileobj)

    entities = EntitySet()
    for definition in entity_definitions:
        entities.register_entity(definition['name'],
                                 definition.get('description', None),
                                 {child['name']: child for child in definition.get('has_a', [])},
                                 definition.get('is_a', None),
                                 definition.get('attributes', None))

    extensions = {}
    for definition in entity_definitions:
        for extension in definition.get('extensions', []):
            if extension in extensions and extensions[extension] != definition['name']:
                msg = 'conflicting extension {} for {} and {}'
                raise ValueError(msg.format(extension, extensions[extension], definition['name']))
            extensions[extension] = definition['name']
    parser = EntityDefinitionParser(extensions)

    provided_entities = []
    for definition in entity_definitions:
        for provided in definition.get('provided', []):
            provided_entities.append(parser.parse_provided_entity(provided.split()))
    return entities, parser, provided_entities
