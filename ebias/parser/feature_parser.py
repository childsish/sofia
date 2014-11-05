import argparse
import re

from argument_dictionary import ArgumentDictionary
from requested_feature import RequestedFeature

class FeatureParser(object):
    """ The parser for features from the command line and from feature files.
        
    The feature string takes the form of:
        -f "[-p PARAM] [-a ATTR] feature [resource]*"
    where
        feature
            is the name of the feature
        resource
            is a list of resources the feature depends upon
        PARAM
            is a list of arguments to the requested feature
        ATTR
            are the attributes of the feature

    An example:
        -f VariantFrequency
        -f "VariantFrequency tmp -p sample=B01P01"
    """
    
    def __init__(self, provided_resources):
        """ Initialise the FeatureParser with a list of resources that the user
        has provided. """
        self.provided_resources = provided_resources
        self.parser = self._defineParser()

    def parseFeatures(self, feature_strings):
        """ Parse all feature strings in a list """
        return [self.parseFeature(feature_string) for feature_string in\
            feature_strings]
    
    def parseFeature(self, feature_string):
        """ Parse a feature string. """
        args = self.parser.parse_args(feature_string.split())
        resource = self._getResource(args.resource, args.feature)
        return RequestedFeature(args.feature, resource, args.param, args.attr)
    
    def _getResource(self, resource, feature_name):
        """ Parse a resource from the feature string and check if any requested
        resources have been provided by the user. """
        try:
            return frozenset(self.provided_resources[r] for r in resource)
        except KeyError, e:
            raise KeyError('Resource "%s" requested by feature "%s" not provided.'%(e.args[0], feature_name))
    
    def _defineParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('feature')
        parser.add_argument('resource', nargs='*')
        parser.add_argument('-p', '--param', action=ArgumentDictionary,
            nargs='+', default={})
        parser.add_argument('-a', '--attr', action=ArgumentDictionary,
            nargs='+', default={})
        return parser
