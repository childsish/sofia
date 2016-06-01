import json

from entity_set import EntitySet
from sofia.workflow_template.entity_definition_parser import EntityDefinitionParser


def load_entity_set(filename):
    with open(filename) as fileobj:
        entity_definitions = json.load(fileobj)

    entities = EntitySet({definition['name']: definition for definition in entity_definitions})
    for definition in entity_definitions:
        if 'has_a' in definition:
            definition['has_a'] = {child['name']: child for child in definition['has_a']}
            for child in definition['has_a']:
                entities.has_a.add_edge(definition['name'], child)
        if 'is_a' in definition:
            entities.is_a.add_edge(definition['is_a'], definition['name'])

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
