class Feature(object):
    
    IN = []
    OUT = []

    def calculate(self):
        raise NotImplementedError('This method must be overridden')
