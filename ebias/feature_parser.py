import re

from requested_feature import RequestedFeature

class FeatureParser(object):
    """ The parser for features from the command line and from feature files.
        
    The feature string takes the form of:
        -f <name>[:(<key>=<value>)+][:<resource>[,<resource>]*]
    where <name>
            is the name of the requested feature,
        (<key>=<value>)+
            is a list of arguments to the requested feature
        <resource>
            is a resource that the requested feature specifically depends upon.
    
    An example:
        -f VariantFrequency:sample=B01P01:tmp
    """
    
    PARTS_REGX = re.compile('(?P<name>[^:]+)' +\
                            '(?::(?P<part1>[^:]+))?' +\
                            '(?::(?P<part2>[^:]+))?')
    
    def __init__(self, provided_resources):
        """ Initialise the FeatureParser with a list of resources that the user
        has provided. """
        self.provided_resources = provided_resources

    def parse(self, line):
        """ Parse a feature string. """
        match = self.PARTS_REGX.match(line)
        name, part1, part2 = match.groups()
        requested_resources = frozenset()
        param = {}
        
        if part2 is not None:
            if '=' in part1 and '=' in part2:
                raise ValueError('Feature initialisation arguments have been defined twice.')
            elif '=' not in part1 and '=' not in part2:
                raise ValueError('Feature requested resources have been defined twice.')
            if '=' in part2:
                param = dict(p.split('=', 1) for p in part2.split(','))
            else:
                requested_resources = self._parseResources(part2, name)
        if part1 is not None:
            if '=' in part1:
                param = dict(p.split('=', 1) for p in part1.split(','))
            else:
                requested_resources = self._parseResources(part1, name)
        return RequestedFeature(name, requested_resources, param)
    
    def _parseResources(self, resource_part, feature_name):
        """ Parse a resource from the feature string and check if any requested
        resources have been provided by the user. """
        try:
            return frozenset([self.provided_resources[r] for r in resource_part.split(',')])
        except KeyError, e:
            raise KeyError('Resource "%s" requested by feature "%s" not provided.'%(e.args[0], feature_name))
