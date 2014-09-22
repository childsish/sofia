import re

from requested_feature import RequestedFeature

class FeatureParser(object):
    """ -f <name>[:(<key>=<value>)+][:<resource>[,<resource>]*]
        -f VariantFrequency:sample=B01P01:tmp
    """
    
    PARTS_REGX = re.compile('(?P<name>[^:]+)' +\
                            '(?::(?P<part1>[^:]+))?' +\
                            '(?::(?P<part2>[^:]+))?')
    
    def __init__(self, provided_resources):
        self.provided_resources = provided_resources

    def parse(self, line):
        match = self.PARTS_REGX.match(line)
        name, part1, part2 = match.groups()
        requested_resources = frozenset()
        init_args = {}
        
        if part2 is not None:
            if '=' in part1 and '=' in part2:
                raise ValueError('Feature initialisation arguments have been defined twice.')
            elif '=' not in part1 and '=' not in part2:
                raise ValueError('Feature requested resources have been defined twice.')
            if '=' in part2:
                init_args = dict(p.split('=', 1) for p in part2.split(','))
            else:
                requested_resources = self._parseResources(part2, name)
        if part1 is not None:
            if '=' in part1:
                init_args = dict(p.split('=', 1) for p in part1.split(','))
            else:
                requested_resources = self._parseResources(part1, name)
        return RequestedFeature(name, requested_resources, init_args)
    
    def _parseResources(self, resource_part, feature_name):
        try:
            return frozenset([self.provided_resources[r] for r in resource_part.split(',')])
        except KeyError, e:
            raise KeyError('Resource "%s" requested by feature "%s" not provided.'%(e.args[0], feature_name))
