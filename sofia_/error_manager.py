class ErrorManager(object):
    """ An object for storing error messages from graph resolution.
    
    This class is intended to be used as a global storage for error messages
    that occur during graph resolution. The ErrorManager is reset before
    each ActionHyperGraph is resolved and errors are accumulated for later
    reporting. 
    """
    def __init__(self):
        self.errors = set()
    
    def reset(self):
        """ Empty the ErrorManager of accumulated error messages. """
        self.errors = set()
        
    def addError(self, msg):
        """ Add an error message to the ErrorManager. """
        self.errors.add(msg)

ERROR_MANAGER = ErrorManager()
