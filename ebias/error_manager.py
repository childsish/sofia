class ErrorManager(object):
    def __init__(self):
        self.errors = set()
    
    def reset(self):
        self.errors = set()
        
    def addError(self, msg):
        self.errors.add(msg)

ERROR_MANAGER = ErrorManager()
