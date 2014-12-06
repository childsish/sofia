import argparse
import re

from argument_dictionary import ArgumentDictionary
from requested_action import RequestedAction

class ActionParser(object):
    """ The parser for steps from the command line and from action files.
        
    The action string takes the form of:
        -f "[-p PARAM] [-a ATTR] action [resource]*"
    where
        action
            is the name of the action
        resource
            is a list of resources the action depends upon
        PARAM
            is a list of arguments to the requested action
        ATTR
            are the attributes of the action

    An example:
        -f VariantFrequency
        -f "VariantFrequency tmp -p sample=B01P01"
    """
    
    def __init__(self, provided_resources):
        """ Initialise the ActionParser with a list of resources that the user
        has provided. """
        self.provided_resources = provided_resources
        self.parser = self._defineParser()

    def parseActions(self, action_strings):
        """ Parse all action strings in a list """
        return [self.parseAction(action_string) for action_string in\
            action_strings if action_string.strip() != '']
    
    def parseAction(self, action_string):
        """ Parse a action string. """
        args = self.parser.parse_args(action_string.split())
        resource = self._getResource(args.resource, args.action)
        return RequestedAction(args.action, resource, args.param, args.attr)
    
    def _getResource(self, resource, action_name):
        """ Parse a resource from the action string and check if any requested
        resources have been provided by the user. """
        try:
            return frozenset(self.provided_resources[r] for r in resource)
        except KeyError, e:
            raise KeyError('Resource "%s" requested by action "%s" not provided.'%(e.args[0], action_name))
    
    def _defineParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('action')
        parser.add_argument('resource', nargs='*')
        parser.add_argument('-p', '--param', action=ArgumentDictionary,
            nargs='+', default={})
        parser.add_argument('-a', '--attr', action=ArgumentDictionary,
            nargs='+', default={})
        return parser
