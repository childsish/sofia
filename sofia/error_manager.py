from collections import defaultdict


class ErrorManager(object):
    """ An object for storing error messages from graph resolution.
    
    This class is intended to be used as a global storage for error messages
    that occur during graph resolution. The ErrorManager is reset before
    each ActionHyperGraph is resolved and errors are accumulated for later
    reporting. 
    """
    def __init__(self):
        self.errors = defaultdict(set)
    
    def reset(self):
        """ Empty the ErrorManager of accumulated error messages. """
        self.errors = defaultdict(set)
        
    def add_error(self, msg, node=''):
        """ Add an error message to the ErrorManager. """
        self.errors[msg].add(node)

ERROR_MANAGER = ErrorManager()
