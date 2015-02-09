import re

from requested_entity import RequestedEntity


class EntityParser(object):
    """ A parser for entity requests.
        
    The entity request takes the form of:
        <entity_request> ::= <entity>[:<header>][:<attribute>[:<attribute>]*]
        <attribute> ::= <key>=<value>[,<value>]*

    where
        <entity>
            is the name of an entity
        <header>
            is the name to use in the header
        <key>
            is the name of an attribute
        <value>
            is the value of an attribute

    Command line examples:
        -e chromosome_id position
        -e gene_id:resource=gencode.gtf,gene_id=ensemble
    """

    REGX = re.compile(r'(?P<entity>[^[.:]+)(?P<getter>[^:]+)?:?(?P<header>[^=]+(:|$))?(?P<attributes>.+)?')
    
    def __init__(self, provided_resources):
        """ Initialise the ActionParser with a list of resources that the user
        has provided. """
        self.provided_resources = provided_resources

    def parse_entity_requests(self, entity_requests):
        """ Parse all entity requests in a list.

        :param entity_requests: a list of entity request strings
        :return: a list of RequestedEntities
        """
        return [self.parse_entity_request(entity_request) for entity_request in
                entity_requests if entity_request.strip() != '']
    
    def parse_entity_request(self, entity_request):
        """ Parse a single entity request.

        :param entity_request: an entity request string
        :return: a RequestedEntity
        """
        match = self.REGX.match(entity_request)
        if match is None:
            raise ValueError('Unrecognised entity request.')
        entity = match.group('entity')
        getter = '' if match.group('getter') is None else match.group('getter')
        header = None if match.group('header') is None else match.group('header')
        attributes = {} if match.group('attributes') is None else\
            {k: sorted(v.split(',')) for k, v in
             (part.split('=', 1) for part in match.group('attributes').split(':'))}
        if 'resource' in attributes:
            resources = self._get_resources(attributes['resource'], entity)
            del attributes['resource']
        else:
            resources = frozenset()
        return RequestedEntity(entity, getter, header, attributes, resources)
    
    def _get_resources(self, resources, entity):
        """ Parse a resource from the action string and check if any requested
        resources have been provided by the user. """
        try:
            return frozenset(self.provided_resources[r] for r in resources)
        except KeyError, e:
            raise KeyError('Resource "{}" requested by entity "{}" not provided.'.format(e.args[0], entity))
